"""Regression coverage for direct embed API access and provider failures."""

import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
import requests
from botocore.exceptions import ClientError, NoCredentialsError
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from rest_framework.test import APIRequestFactory, force_authenticate

from panorama_openedx_backend.models import DashboardType, UserAccessConfiguration
from panorama_openedx_backend.views import GetDashboardEmbedUrl, GetStudioEmbedUrl, get_student_full_name


def call(view, user=None):
    """Invoke a real DRF permission/exception boundary."""
    request = APIRequestFactory().get('/')
    if user is not None:
        force_authenticate(request, user=user)
    return view.as_view()(request)


@pytest.fixture(name='learner')
def learner_fixture(settings, db):  # pylint: disable=unused-argument
    """Provide an ordinary learner in the supported HTTPS custom mode."""
    settings.PANORAMA_MODE = 'CUSTOM'
    settings.PANORAMA_ENABLE_STUDENT_VIEW = False
    settings.HTTPS = 'on'
    return get_user_model().objects.create_user(username='learner')


@pytest.mark.parametrize('view', [GetDashboardEmbedUrl, GetStudioEmbedUrl])
def test_anonymous_cannot_embed(view):
    """Anonymous callers never reach AWS."""
    with patch('panorama_openedx_backend.views.boto3.Session') as session:
        assert call(view).status_code in (401, 403)
        session.assert_not_called()


@pytest.mark.parametrize('mode', ['DEMO', 'FREE', 'SAAS', 'CUSTOM'])
@pytest.mark.parametrize('view', [GetDashboardEmbedUrl, GetStudioEmbedUrl])
def test_unassigned_user_denied_before_provider(learner, settings, mode, view):
    """Direct URL access cannot bypass dashboard grants in any mode."""
    settings.PANORAMA_MODE = mode
    with patch('panorama_openedx_backend.views.boto3.Session') as session, \
            patch('panorama_openedx_backend.views.requests.request') as request:
        assert call(view, learner).status_code == 403
        session.assert_not_called()
        request.assert_not_called()


@pytest.mark.parametrize('mode', ['SAAS', 'CUSTOM'])
@pytest.mark.parametrize('kind', ['student', 'reader', 'author', 'superuser'])
def test_access_matrix(learner, settings, mode, kind):
    """Dashboard access and console authorship remain separate grants."""
    settings.PANORAMA_MODE = mode
    settings.PANORAMA_ENABLE_STUDENT_VIEW = kind == 'student'
    if kind in ('reader', 'author'):
        group = DashboardType.objects.create(name='staff')
        UserAccessConfiguration.objects.create(user=learner, dashboard_type=group, role=kind.upper())
    if kind == 'superuser':
        learner.is_superuser = True
        learner.save()
    provider = 'get_saas_dashboards' if mode == 'SAAS' else 'get_quicksight_dashboards'
    with patch(f'panorama_openedx_backend.views.{provider}', return_value=[]) as fetch:
        assert call(GetDashboardEmbedUrl, learner).status_code == 200
        fetch.assert_called_once_with(learner)
    with patch('panorama_openedx_backend.views.get_user_arn', return_value=None) as arn:
        assert call(GetStudioEmbedUrl, learner).status_code == (400 if kind == 'author' else 403)
        assert arn.called == (kind == 'author')


@pytest.mark.parametrize('error,status', [
    (requests.exceptions.HTTPError('secret'), 502),
    (requests.exceptions.Timeout('secret'), 504),
    (requests.exceptions.ConnectionError('secret'), 502),
    (json.JSONDecodeError('secret', '', 0), 502),
    (NoCredentialsError(), 502),
    (ClientError({'Error': {'Code': 'AccessDeniedException', 'Message': 'secret'}}, 'GenerateEmbedUrl'), 502),
    (ValueError('secret'), 400),
    (KeyError('EmbedUrl'), 502),
])
def test_dashboard_provider_failures_are_safe(learner, error, status):
    """Expected provider failures return useful status codes without secrets."""
    learner.is_superuser = True
    with patch('panorama_openedx_backend.views.get_quicksight_dashboards', side_effect=error):
        response = call(GetDashboardEmbedUrl, learner)
    assert response.status_code == status
    assert 'secret' not in str(response.data)


@pytest.mark.parametrize('status', [401, 403, 500])
def test_http_error_with_falsey_response(learner, status):
    """Requests treats error responses as falsey, but their status still matters."""
    learner.is_superuser = True
    upstream = requests.Response()
    upstream.status_code = status
    upstream._content = b'secret'  # pylint: disable=protected-access
    with patch('panorama_openedx_backend.views.get_quicksight_dashboards',
               side_effect=requests.exceptions.HTTPError(response=upstream)):
        response = call(GetDashboardEmbedUrl, learner)
    assert response.status_code == (status if status in (401, 403) else 502)
    assert 'secret' not in str(response.data)


def test_unsupported_mode_is_http_error(learner, settings):
    """Report the resolved invalid mode with an actual HTTP failure."""
    learner.is_superuser = True
    settings.PANORAMA_MODE = 'UNKNOWN'
    response = call(GetDashboardEmbedUrl, learner)
    assert response.status_code == 400
    assert response.data['body'] == "Unsupported Panorama mode 'UNKNOWN'"


def test_missing_profile_falls_back():
    """An absent profile should not prevent embedding."""
    assert get_student_full_name(SimpleNamespace(username='learner')) == 'learner'


@pytest.mark.parametrize('https', ['on', 'off'])
def test_author_console_embedding(learner, settings, https):
    """Only HTTPS author sessions generate a console URL."""
    settings.HTTPS = https
    settings.PANORAMA_AWS_ACCESS_KEY = 'key'
    settings.PANORAMA_AWS_SECRET_ACCESS_KEY = 'secret'
    settings.PANORAMA_REGION = 'us-east-1'
    settings.PANORAMA_AWS_ACCOUNT_ID = '123456789012'
    settings.LMS_BASE = 'courses.example.com'
    group = DashboardType.objects.create(name='authors')
    UserAccessConfiguration.objects.create(user=learner, dashboard_type=group, role='AUTHOR', arn='author-arn')
    with patch('panorama_openedx_backend.views.boto3.Session') as session:
        generate = session.return_value.client.return_value.generate_embed_url_for_registered_user
        generate.return_value = {'EmbedUrl': 'https://example.com/console'}
        response = call(GetStudioEmbedUrl, learner)
        if https == 'on':
            assert response.status_code == 200
            assert generate.call_args.kwargs['UserArn'] == 'author-arn'
            assert 'QuickSightConsole' in generate.call_args.kwargs['ExperienceConfiguration']
            generate.side_effect = NoCredentialsError()
            assert call(GetStudioEmbedUrl, learner).status_code == 502
        else:
            assert response.status_code == 421
            session.assert_not_called()


@pytest.mark.django_db(transaction=True)
def test_reader_migration_repairs_only_known_spelling():
    """Run the real migration against historical rows and preserve authors."""
    executor = MigrationExecutor(connection)
    old = [('panorama_openedx_backend', '0007_remove_ai_author_role')]
    new = [('panorama_openedx_backend', '0008_normalize_reader_role')]
    executor.migrate(old)
    apps = executor.loader.project_state(old).apps
    user_model = apps.get_model('auth', 'User')
    access_model = apps.get_model('panorama_openedx_backend', 'UserAccessConfiguration')
    group = apps.get_model('panorama_openedx_backend', 'DashboardType').objects.create(name='test')
    for index, role in enumerate(['Reader', 'READER', 'AUTHOR']):
        user = user_model.objects.create(username=f'user-{index}')
        access_model.objects.create(user=user, dashboard_type=group, role=role)
    try:
        executor = MigrationExecutor(connection)
        executor.migrate(new)
        assert list(UserAccessConfiguration.objects.order_by('user_id').values_list('role', flat=True)) == [
            'READER', 'READER', 'AUTHOR',
        ]
        assert UserAccessConfiguration._meta.get_field('role').default == 'READER'
    finally:
        MigrationExecutor(connection).migrate(new)


@pytest.mark.parametrize('mode', ['DEMO', 'FREE', 'SAAS'])
@pytest.mark.parametrize('payload', [
    None, 1, 'secret', {}, {'body': []}, [None], [1], [[]], [{}],
    [{'url': None}], [{'url': 1}], [{'url': []}], [{'url': ''}],
    [{'url': 'https://example.com/embed', 'name': []}],
])
def test_http_provider_malformed_json_shapes(learner, settings, mode, payload):
    """Valid JSON with invalid dashboard shapes is a safe provider failure."""
    settings.PANORAMA_MODE = mode
    settings.LMS_BASE = 'courses.example.com'
    settings.PANORAMA_AWS_ACCESS_KEY = 'key'
    settings.PANORAMA_AWS_SECRET_ACCESS_KEY = 'secret'
    learner.is_superuser = True
    response = Mock(status_code=200, content=json.dumps(payload).encode())
    with patch('panorama_openedx_backend.views.requests.request', return_value=response), \
            patch('panorama_openedx_backend.views.SigV4Request') as signed:
        signed.return_value.get.return_value = response
        result = call(GetDashboardEmbedUrl, learner)
    assert result.status_code == 502
    assert 'secret' not in str(result.data)


@pytest.mark.parametrize('view', [GetDashboardEmbedUrl, GetStudioEmbedUrl])
@pytest.mark.parametrize('payload', [None, 1, [], {}, {'EmbedUrl': None}, {'EmbedUrl': 1}, {'EmbedUrl': []}])
def test_sdk_provider_malformed_json_shapes(learner, settings, view, payload):
    """Validate the SDK response before student URL processing or console output."""
    settings.PANORAMA_AWS_ACCESS_KEY = 'key'
    settings.PANORAMA_AWS_SECRET_ACCESS_KEY = 'secret'
    settings.PANORAMA_REGION = 'us-east-1'
    settings.PANORAMA_AWS_ACCOUNT_ID = '123456789012'
    settings.LMS_BASE = 'courses.example.com'
    group = DashboardType.objects.create(name='authors')
    UserAccessConfiguration.objects.create(user=learner, dashboard_type=group, role='AUTHOR', arn='author-arn')
    dashboard = {'id': 'student', 'name': 'student', 'displayName': 'Student', 'student_view': True}
    with patch('panorama_openedx_backend.views.boto3.Session') as session, \
            patch('panorama_openedx_backend.views.get_user_dashboards', return_value=[dashboard]):
        session.return_value.client.return_value.generate_embed_url_for_registered_user.return_value = payload
        result = call(view, learner)
    assert result.status_code == 502


@pytest.mark.parametrize('payload', [[], [{'url': 'https://example.com/embed'}], [
    {'url': 'https://example.com/embed', 'name': 'dashboard', 'displayName': 'Dashboard', 'id': '123'},
]])
def test_provider_valid_payload_metadata_preserved(learner, settings, payload):
    """Accept empty assignments and existing URL-only and named provider entries."""
    settings.PANORAMA_MODE = 'DEMO'
    settings.LMS_BASE = 'courses.example.com'
    learner.is_superuser = True
    with patch('panorama_openedx_backend.views.requests.request',
               return_value=Mock(status_code=200, content=json.dumps(payload).encode())):
        result = call(GetDashboardEmbedUrl, learner)
    assert result.status_code == 200
    assert result.data['body'] == payload

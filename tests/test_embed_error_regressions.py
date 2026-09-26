"""Regression coverage for safe provider diagnostics and transport failures."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
import requests
from botocore.exceptions import ClientError

from panorama_openedx_backend.views import GetDashboardEmbedUrl, GetStudioEmbedUrl, embed_error_response


@pytest.mark.parametrize('code,status', [('AccessDeniedException', 403), ('ThrottlingException', 429)])
def test_aws_error_logs_only_diagnostic_codes(caplog, code, status):
    """AWS errors remain distinguishable without logging sensitive payloads."""
    error = ClientError({
        'Error': {'Code': code, 'Message': 'secret-message'},
        'ResponseMetadata': {'HTTPStatusCode': status, 'HTTPHeaders': {'secret-header': 'secret-value'}},
    }, 'GenerateEmbedUrl')
    response = embed_error_response(error)
    assert response.status_code == 502
    assert f'error_code={code}' in caplog.text
    assert f'status_code={status}' in caplog.text
    assert 'secret' not in caplog.text
    assert 'secret' not in str(response.data)


@pytest.mark.parametrize('status', [401, 403, 500])
def test_http_error_logs_status_without_body_or_url(caplog, status):
    """Falsey HTTP error responses retain their status in safe diagnostics."""
    upstream = requests.Response()
    upstream.status_code = status
    upstream.url = 'https://example.com/?token=secret-token'
    upstream._content = b'secret-body'  # pylint: disable=protected-access
    response = embed_error_response(requests.exceptions.HTTPError('secret-message', response=upstream))
    assert response.status_code == (status if status in (401, 403) else 502)
    assert f'status_code={status}' in caplog.text
    assert 'secret' not in caplog.text
    assert 'secret' not in str(response.data)


@pytest.mark.parametrize('mode', ['DEMO', 'FREE', 'SAAS'])
def test_invalid_provider_encoding_is_bad_gateway(settings, mode):
    """Malformed bytes exercise JSON decoding through each HTTP provider."""
    settings.PANORAMA_MODE = mode
    settings.HTTPS = 'on'
    settings.LMS_BASE = 'courses.example.com'
    settings.PANORAMA_AWS_ACCESS_KEY = 'key'
    settings.PANORAMA_AWS_SECRET_ACCESS_KEY = 'secret'
    upstream = Mock(status_code=200, content=b'\xffsecret')
    request = SimpleNamespace(user=SimpleNamespace(username='learner'))
    with patch('panorama_openedx_backend.views.requests.request', return_value=upstream), \
            patch('panorama_openedx_backend.views.SigV4Request') as signed, \
            patch('panorama_openedx_backend.views.get_user_role', return_value='READER'):
        signed.return_value.get.return_value = upstream
        response = GetDashboardEmbedUrl().get(request)
    assert response.status_code == 502
    assert 'secret' not in str(response.data)


@pytest.mark.parametrize('view', [GetDashboardEmbedUrl, GetStudioEmbedUrl])
def test_http_session_rejected_before_contacting_provider(settings, view):
    """A missing HTTPS session is a bad request, not HTTP/2 misdirection."""
    settings.HTTPS = 'off'
    with patch('panorama_openedx_backend.views.boto3.Session') as session, \
            patch('panorama_openedx_backend.views.panorama_mode') as mode:
        response = view().get(SimpleNamespace())
    assert response.status_code == 400
    assert 'HTTPS' in str(response.data)
    session.assert_not_called()
    if view is GetDashboardEmbedUrl:
        mode.assert_not_called()

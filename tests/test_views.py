"""
Tests for QuickSight dashboard URL handling.
"""

from unittest.mock import Mock, patch
from urllib.parse import parse_qsl, urlsplit

import pytest
from django.contrib.auth import get_user_model

from panorama_openedx_backend.models import Dashboard, DashboardType
from panorama_openedx_backend.utils import get_student_dashboards
from panorama_openedx_backend.views import add_student_parameters, get_quicksight_dashboards

User = get_user_model()


@pytest.mark.django_db
def test_get_student_dashboards_marks_dashboards_as_student_view():
    """
    Student dashboards should be tagged so the embed layer can inject learner parameters.
    """
    dashboard = Dashboard.objects.create(
        dashboard_id='student-dashboard',
        name='student-dashboard',
        display_name='Student dashboard',
        priority=1,
    )
    dashboard_type = DashboardType.objects.create(name='students', student_view=True)
    dashboard_type.dashboards.add(dashboard)

    dashboards = get_student_dashboards()

    assert dashboards == [{
        'name': 'student-dashboard',
        'displayName': 'Student dashboard',
        'id': 'student-dashboard',
        'student_view': True,
    }]


@pytest.mark.django_db
@patch('panorama_openedx_backend.views.boto3.Session')
@patch('panorama_openedx_backend.views.get_user_dashboards')
def test_get_quicksight_dashboards_adds_student_parameters(
    mock_get_user_dashboards,
    mock_session,
    settings,
):
    """
    Student dashboard embed URLs must carry userId and lms parameters.
    """
    settings.PANORAMA_AWS_ACCESS_KEY = 'key'
    settings.PANORAMA_AWS_SECRET_ACCESS_KEY = 'secret'
    settings.PANORAMA_REGION = 'us-east-1'
    settings.PANORAMA_AWS_ACCOUNT_ID = '123456789012'
    settings.PANORAMA_DEFAULT_USER_ARN = 'arn:aws:quicksight:us-east-1:123456789012:user/default/student'
    settings.LMS_BASE = 'courses.example.com'
    settings.PANORAMA_MODE = 'CUSTOM'

    user = User.objects.create_user(username='student-01')
    mock_get_user_dashboards.return_value = [{
        'name': 'student-dashboard',
        'displayName': 'Student dashboard',
        'id': 'dashboard-1',
        'student_view': True,
    }]

    quicksight_client = Mock()
    quicksight_client.generate_embed_url_for_registered_user.return_value = {
        'EmbedUrl': 'https://quicksight.aws.amazon.com/embed/registered/dashboard-1'
    }
    mock_session.return_value.client.return_value = quicksight_client

    dashboards = get_quicksight_dashboards(user)

    assert dashboards == [{
        'name': 'student-dashboard',
        'displayName': 'Student dashboard',
        'id': 'dashboard-1',
        'url': (
            'https://quicksight.aws.amazon.com/embed/registered/dashboard-1'
            f'#p.userId={user.id}&p.lms=courses.example.com'
        ),
    }]


def test_add_student_parameters_preserves_existing_fragment(settings):
    """
    Student parameters should be appended to existing fragment state.
    """
    settings.LMS_BASE = 'courses.example.com'
    user = Mock(id=42)

    updated_url = add_student_parameters(
        'https://quicksight.aws.amazon.com/embed/dashboard#sheet=abc',
        user,
    )

    fragment_params = dict(parse_qsl(urlsplit(updated_url).fragment))

    assert fragment_params == {
        'sheet': 'abc',
        'p.userId': '42',
        'p.lms': 'courses.example.com',
    }

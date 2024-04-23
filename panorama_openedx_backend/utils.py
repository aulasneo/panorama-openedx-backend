"""
Utility functions to access the Panorama configurations.
"""

from django.contrib.auth import get_user_model
from .models import UserAccessConfiguration

User = get_user_model()


def has_access_to_panorama(user: User) -> bool:
    """
    Returns true if the user can access Panorama, i.e., if there is a record in the
    user access configuration model.
    """

    return UserAccessConfiguration.objects.filter(user=user).exists()


def get_user_role(user: User) -> str:
    """
    Get the Panorama user role
    """

    user_access_configuration = UserAccessConfiguration.objects.get(user=user)

    return user_access_configuration.role


def get_user_arn(user: User) -> str:
    """
    Get the AWS user ARN mapping to this user
    """

    user_access_configuration = UserAccessConfiguration.objects.get(user=user)

    return user_access_configuration.arn


def get_user_dashboards(user: User) -> list:
    """
    Get the list of user dashboards to import
    """

    user_access_configuration = UserAccessConfiguration.objects.get(user=user)
    dashboard_type = user_access_configuration.dashboard_type

    dashboard_list = []
    for dashboard in dashboard_type.dashboards.all():
        dashboard_list.append({
            "name": dashboard.name,
            "displayName": dashboard.display_name,
            "id": dashboard.dashboard_id,
        })

    return dashboard_list

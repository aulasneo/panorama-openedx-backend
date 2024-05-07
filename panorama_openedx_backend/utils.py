"""
Utility functions to access the Panorama configurations.
"""
from django.contrib.auth import get_user_model

from .models import UserAccessConfiguration

User = get_user_model()


def has_access_to_panorama(user: User) -> bool:
    """
    Has access to panorama function.

    Return true if the user can access Panorama, i.e., if there is a record in the user access configuration model.
    """
    return UserAccessConfiguration.objects.filter(user=user).exists() or user.is_superuser


def get_user_role(user: User) -> str:
    """
    Get user role function.

    Get the Panorama user role.
    """
    user_access_configuration = UserAccessConfiguration.objects.get(user=user)

    if user_access_configuration:
        return user_access_configuration.role
    else:
        if user.is_superuser:
            return "READER"


def get_user_arn(user: User) -> str:
    """
    Get user arn function.

    Get the AWS user ARN mapping to this user.
    """
    user_access_configuration = UserAccessConfiguration.objects.get(user=user)

    return user_access_configuration.arn


def get_user_dashboards(user: User) -> list:
    """
    Get user dashboards function.

    Get the list of user dashboards to import.
    """
    user_access_configuration = UserAccessConfiguration.objects.get(user=user)
    dashboard_type = user_access_configuration.dashboard_type

    dashboard_list = []
    for dashboard in dashboard_type.dashboards.all().order_by('priority'):
        dashboard_list.append({
            "name": dashboard.name,
            "displayName": dashboard.display_name,
            "id": dashboard.dashboard_id,
        })

    return dashboard_list


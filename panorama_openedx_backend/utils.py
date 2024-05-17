"""
Utility functions to access the Panorama configurations.
"""
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import UserAccessConfiguration

User = get_user_model()


def panorama_mode() -> str:
    """
    Returns the Panorama mode.
    """

    return settings.PANORAMA_MODE


def has_access_to_panorama(user: User, mode: str) -> bool:
    """
    Has access to panorama function.

    Return true if the user can access Panorama, i.e., if there is a record in the user access configuration model
    or if the user is superuser.
    In DEMO mode, the backend may not be initialized so only superusers have access.
    """

    if mode == 'DEMO':
        return user.is_superuser
    else:
        return UserAccessConfiguration.objects.filter(user=user).exists() or user.is_superuser


def get_user_role(user: User, mode: str) -> str:
    """
    Get the Panorama user role.
    In DEMO mode, the backend may not be initialized so superusers have READ access.

    """

    if mode == 'DEMO':
        return "READER" if user.is_superuser else None
    else:
        user_access_configuration = UserAccessConfiguration.objects.get(user=user)

        if user_access_configuration:
            return user_access_configuration.role
        else:
            return "READER" if user.is_superuser else None


def get_user_arn(user: User) -> str:
    """
    Get the AWS user ARN mapping to this user.
    """
    user_access_configuration = UserAccessConfiguration.objects.get(user=user)

    return user_access_configuration.arn


def get_user_dashboards(user: User) -> list:
    """
    Get the list of user dashboards to import from the Django admin configuration.
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

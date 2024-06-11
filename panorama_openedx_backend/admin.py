"""
Admin settings for Panorama Open edX backend.

written by:     Andrés González
                https://aulasneo.com

date:           April 2024

usage:          register the custom Django models in LMS Django Admin
"""
import logging

from django.conf import settings
from django.contrib import admin

from .models import Dashboard, DashboardType, UserAccessConfiguration

logger = logging.getLogger(__name__)


class DashboardAdmin(admin.ModelAdmin):
    """
    Dashboard admin class.
    """

    list_display = [
        "priority",
        "dashboard_id",
        "name",
        "display_name",
    ]
    ordering = ("priority",)


class DashboardTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "student_view"]
    filter_horizontal = ["dashboards"]


class UserAccessConfigurationAdmin(admin.ModelAdmin):
    list_display = ["user", "dashboard_type", "arn", "role"]


panorama_mode = getattr(settings, 'PANORAMA_MODE', 'DEMO')
if panorama_mode in ['SAAS', 'CUSTOM']:
    logger.info(f"Registering Panorama admin for mode '{panorama_mode}'")
    admin.site.register(Dashboard, DashboardAdmin)
    admin.site.register(DashboardType, DashboardTypeAdmin)
    admin.site.register(UserAccessConfiguration, UserAccessConfigurationAdmin)
else:
    logger.info(f"Panorama mode {panorama_mode}. Skipping admin interface registration")

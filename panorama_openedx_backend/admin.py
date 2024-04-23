"""
Admin settings for Panorama Open edX backend.

written by:     Andrés González
                https://aulasneo.com

date:           April 2024

usage:          register the custom Django models in LMS Django Admin
"""
import logging

from django.contrib import admin

from .models import Dashboard, DashboardType, UserAccessConfiguration

logger = logging.getLogger(__name__)


class DashboardAdmin(admin.ModelAdmin):
    list_display = [
        "dashboard_id",
        "name",
        "display_name",
    ]


class DashboardTypeAdmin(admin.ModelAdmin):
    list_display = ["name"]
    filter_horizontal = ["dashboards"]


class UserAccessConfigurationAdmin(admin.ModelAdmin):
    list_display = ["user", "dashboard_type", "arn", "role"]


logger.debug("Registering Panorama admin")
admin.site.register(Dashboard, DashboardAdmin)
admin.site.register(DashboardType, DashboardTypeAdmin)
admin.site.register(UserAccessConfiguration, UserAccessConfigurationAdmin)

"""
URLs for panorama_openedx_backend.
"""
from django.urls import re_path  # pylint: disable=unused-import

from panorama_openedx_backend.api.views import GetDashboardEmbedUrl, GetUserAccess, GetUserRole

urlpatterns = [
    # TODO: Fill in URL patterns and views here.
    re_path(r'get-embed-url', GetDashboardEmbedUrl.as_view(), name='get dashboard embed url'),
    re_path(r'get-user-access', GetUserAccess.as_view(), name='get user access url'),
    re_path(r'get-user-role', GetUserRole.as_view(), name='get user role url'),
]

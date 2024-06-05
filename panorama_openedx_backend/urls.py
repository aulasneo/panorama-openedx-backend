"""
URLs for panorama_openedx_backend.
"""
from django.urls import re_path

from panorama_openedx_backend.views import GetDashboardEmbedUrl, GetPanoramaMode, GetUserAccess, GetUserRole

urlpatterns = [
    # TODO: Fill in URL patterns and views here.
    re_path(r'get-embed-url', GetDashboardEmbedUrl.as_view(), name='get dashboard embed url'),
    re_path(r'get-user-access', GetUserAccess.as_view(), name='get user access url'),
    re_path(r'get-user-role', GetUserRole.as_view(), name='get user role url'),
    re_path(r'get-panorama-mode', GetPanoramaMode.as_view(), name='get Panorama mode'),
]

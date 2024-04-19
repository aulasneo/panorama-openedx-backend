"""
URLs for panorama_openedx_backend.
"""
from django.urls import re_path  # pylint: disable=unused-import

from panorama_openedx_backend.api.views import GetDashboardEmbedUrl


urlpatterns = [
    # TODO: Fill in URL patterns and views here.
    re_path(r'', GetDashboardEmbedUrl.as_view(), name='get dashboard embed url'),
]

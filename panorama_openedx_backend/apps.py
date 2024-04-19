"""
panorama_openedx_backend Django application initialization.
"""

from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class PanoramaOpenedxBackendConfig(AppConfig):
    """
    Configuration for the panorama_openedx_backend Django application.
    """

    name = 'panorama_openedx_backend'

    plugin_app = {
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
            },
        },
    }

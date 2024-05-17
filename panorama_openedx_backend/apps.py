"""
panorama_openedx_backend Django application initialization.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class PanoramaOpenedxBackendConfig(AppConfig):
    """
    Configuration for the panorama_openedx_backend Django application.
    """

    name = 'panorama_openedx_backend'

    plugin_app = {
        'url_config': {
            'lms.djangoapp': {
                'namespace': 'panorama',
                'regex': 'panorama/api',
                'relative_path': 'urls',
            },
        },

        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
            },
        },
    }

    logger.info("Panorama backend initialized")

"""
panorama_openedx_backend Django application views.
"""
import json
import logging
from urllib.parse import urlencode, urlsplit, urlunsplit

import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from panorama_openedx_backend.aws_sigv4_query.api import SigV4Request
from panorama_openedx_backend.utils import (
    get_user_arn,
    get_user_dashboards,
    get_user_role,
    has_access_to_panorama,
    panorama_mode,
)

from . import __version__

logger = logging.getLogger(__name__)

DEMO_DASHBOARDS_HOST = 'panorama-get-demo-dashboards.aulasneo.link'
FREE_DASHBOARDS_HOST = 'panorama-get-free-dashboards.aulasneo.link'
SAAS_DASHBOARDS_HOST = 'panorama-get-saas-dashboards.aulasneo.link'


def add_student_parameters(embed_url: str, user) -> str:
    """
    Append the parameters required by student dashboards to the embed URL fragment.
    """
    student_params = urlencode([
        ('p.userId', user.id),
        ('p.lms', settings.LMS_BASE),
    ])
    url_parts = urlsplit(embed_url)
    fragment = f'{url_parts.fragment}&{student_params}' if url_parts.fragment else student_params
    return urlunsplit(url_parts._replace(fragment=fragment))


def get_quicksight_dashboards(user):
    """
    Get the dashboards of the logged-in user directly from Quicksight.
    """
    session = boto3.Session(
        aws_access_key_id=settings.PANORAMA_AWS_ACCESS_KEY,
        aws_secret_access_key=settings.PANORAMA_AWS_SECRET_ACCESS_KEY
    )

    quicksight = session.client(
        "quicksight",
        region_name=settings.PANORAMA_REGION,
    )

    # CHECKING IF USER HAS A ARN SET
    quicksight_arn = get_user_arn(user)
    if not quicksight_arn:
        raise ValueError('Unassigned user ARN')

    # CHECKING IF USER HAS A DASHBOARD TYPE SET
    dashboards_of_user = get_user_dashboards(user)
    if not dashboards_of_user:
        raise ValueError('Dashboard not assigned to user')

    # CHECKING IF USER HAS A ROLE SET
    user_role = get_user_role(user)
    if not user_role:
        raise ValueError('User role not assigned')

    for dashboard in dashboards_of_user:

        experience_config = {
            'Dashboard': {
                'InitialDashboardId': dashboard['id'],
            }
        }

        response = quicksight.generate_embed_url_for_registered_user(
            AllowedDomains=[f"https://*.{settings.LMS_BASE}"],
            AwsAccountId=settings.PANORAMA_AWS_ACCOUNT_ID,
            SessionLifetimeInMinutes=123,
            UserArn=quicksight_arn,
            ExperienceConfiguration=experience_config
        )
        dashboard['url'] = response['EmbedUrl']
        if dashboard.get('student_view'):
            dashboard['url'] = add_student_parameters(dashboard['url'], user)
        dashboard.pop('student_view', None)

    return dashboards_of_user


def get_demo_dashboards(user) -> dict:
    """
    Get the demo dashboards from the Aulasneo Panorama API.
    """
    lms_base = settings.LMS_BASE

    if lms_base in ['localhost', 'local.overhang.io', 'local.edly.io']:
        raise requests.exceptions.HTTPError('Panorama will not work in testing or development environments.')

    if settings.HTTPS != 'on':
        raise requests.exceptions.HTTPError('Panorama is only supported from HTTPS sessions.')

    method = 'GET'
    url = 'https://' + DEMO_DASHBOARDS_HOST + '/get-demo-dashboards'
    params = {
        'lms': lms_base,
        'user': user.username,
        'version': __version__,
        'dashboard_function': 'READER',
    }

    response = requests.request(
        method=method, url=url,
        data={},
        timeout=30,
        params=params)
    if response.status_code != 200:
        logger.error(f'Panorama error {response.status_code} getting demo dashboards: {response.content}')
    response.raise_for_status()

    dashboards = json.loads(response.content)

    return dashboards


def make_signed_get(host: str, uri: str, user) -> dict:
    """
    Use Signed V4 requests to make a signed call to an AWS API gateway.
    """
    sigv4_request = SigV4Request(
        access_key=settings.PANORAMA_AWS_ACCESS_KEY,
        secret_key=settings.PANORAMA_AWS_SECRET_ACCESS_KEY,
        region='us-east-1',
    )

    response = sigv4_request.get(
        host=host,
        uri=uri,
        lms=settings.LMS_BASE,
        user=user.username,
        version=__version__,
        dashboard_function=get_user_role(user)
    )
    response.raise_for_status()

    return json.loads(response.content)


def get_free_dashboards(user) -> dict:
    """
    Get the free dashboards from the Aulasneo Panorama API.

    This call must be signed by the AWS user configured.
    """
    if settings.HTTPS != 'on':
        raise ValueError('Only supported in HTTPS sessions.')

    dashboards = make_signed_get(FREE_DASHBOARDS_HOST, 'get-free-dashboards', user)
    return dashboards


def get_saas_dashboards(user) -> dict:
    """
    Get the SaaS dashboards from the Aulasneo Panorama API.

    This call must be signed by the AWS user configured.
    """
    if settings.HTTPS != 'on':
        raise ValueError('Only supported in HTTPS sessions.')

    dashboards = make_signed_get(SAAS_DASHBOARDS_HOST, 'get-saas-dashboards', user)
    return dashboards


class GetDashboardEmbedUrl(APIView):
    """
    Get dashboard embed url.

    View that returns the Panorama dashboads embed URLs for the session's user,
    depending on the Panorama mode configured.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Get dashboard embed url function.
        """
        if settings.HTTPS != 'on':
            return Response(
                status=421,
                data="HTTP not supported. Use only HTTPS."
            )

        try:
            mode = panorama_mode()

            if mode == 'DEMO':
                dashboards_of_user = get_demo_dashboards(request.user)

            elif mode == 'FREE':
                dashboards_of_user = get_free_dashboards(request.user)

            elif mode == 'SAAS':
                dashboards_of_user = get_saas_dashboards(request.user)

            elif mode == 'CUSTOM':
                dashboards_of_user = get_quicksight_dashboards(request.user)

            else:
                return Response({
                    'statusCode': 400,
                    'body': f"Unsupported Panorama mode '{panorama_mode}'"
                })

        except requests.exceptions.HTTPError as e:
            if hasattr(e, 'response'):
                err_code = e.response.status_code
                msg = e.response.text
            else:
                err_code = 400
                msg = e.strerror
            return Response(
                status=err_code,
                data=msg
            )

        return Response({
            'statusCode': 200,
            'body': dashboards_of_user
        })


class GetStudioEmbedUrl(APIView):
    """
    Returns a QuickSight Console (AUTHOR) embed URL.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Handle GET request to retrieve QuickSight Console embed URL.
        """
        try:
            quicksight_arn = get_user_arn(request.user)
            if not quicksight_arn:
                return Response({"error": "User ARN not assigned"}, status=400)

            session = boto3.Session(
                aws_access_key_id=settings.PANORAMA_AWS_ACCESS_KEY,
                aws_secret_access_key=settings.PANORAMA_AWS_SECRET_ACCESS_KEY
            )

            quicksight = session.client(
                "quicksight",
                region_name=settings.PANORAMA_REGION,
            )

            experience_config = {
                "QuickSightConsole": {
                    "InitialPath": "/start",
                    "FeatureConfigurations": {
                        "StatePersistence": {"Enabled": True}
                    }
                }
            }

            response = quicksight.generate_embed_url_for_registered_user(
                AllowedDomains=[f"https://*.{settings.LMS_BASE}"],
                AwsAccountId=settings.PANORAMA_AWS_ACCOUNT_ID,
                SessionLifetimeInMinutes=120,
                UserArn=quicksight_arn,
                ExperienceConfiguration=experience_config,
            )

            return Response(
                {
                    "statusCode": 200,
                    "body": [{
                        "name": "console",
                        "displayName": "Console",
                        "url": response["EmbedUrl"]
                    }]
                }
            )

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Error generating console URL: {str(e)}")
            return Response({"error": str(e)}, status=500)


class GetUserAccess(APIView):
    """
    Get user access view.

    View that checks if the users can access Panorama.
    A user can access Panorama if it is superuser or has a record in the Django admin configuration.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Get user access.
        """
        return Response({
            'statusCode': 200,
            'body': has_access_to_panorama(request.user)
        })


class GetUserRole(APIView):
    """
    Retrieve the user role (READER, AUTHOR, etc.) from the Panorama Django admin configuration.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Get user role.
        """
        return Response({
            'statusCode': 200,
            'body': get_user_role(request.user),
        })


class GetPanoramaMode(APIView):
    """
    View that checks if the users can access Panorama.

    A user can access Panorama if it is superuser or has a record in the Django admin configuration.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Get Panorama mode.
        """
        return Response({
            'statusCode': 200,
            'body': panorama_mode()
        })

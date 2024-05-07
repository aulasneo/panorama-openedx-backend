"""
panorama_openedx_backend Django application views.
"""

import boto3
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.error import HTTPError

from panorama_openedx_backend.utils import get_user_arn, get_user_dashboards, get_user_role, has_access_to_panorama


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

    """
    getDashboardFreeApi?lms=example.com
    getDashboardDemoApi
    getDashboardSaasApi?lms=example.com&
    """

    # CHECKING IF USER HAS A ARN SET
    quicksight_arn = get_user_arn(user)
    if not quicksight_arn:
        raise HTTPError(code=403, msg='Forbidden')

    # CHECKING IF USER HAS A DASHBOARD TYPE SET
    dashboards_of_user = get_user_dashboards(user)
    if not dashboards_of_user:
        raise HTTPError(code=404, msg='Dashboard not assigned to user')

    # CHECKING IF USER HAS A ROLE SET
    user_role = get_user_role(user)
    if not user_role:
        raise HTTPError(code=404, msg='User role not assigned')

    for dashboard in dashboards_of_user:

        # SETTING EXPERIENCE CONFIG ACCORDING TO USER ROLE
        if user_role == "READER":
            experience_config = {
                'Dashboard': {
                    'InitialDashboardId': dashboard['id'],
                }
            }

        elif user_role == "AUTHOR":
            experience_config = {
                'QuickSightConsole': {
                    'InitialPath': "/start",
                    'FeatureConfigurations': {
                        'StatePersistence': {
                            'Enabled': True
                        },
                    },
                }
            }

        elif user_role == "AI_AUTHOR":
            experience_config = {
                'QSearchBar': {
                    'InitialTopicId': "CVomHyE9Wf06YnPHcaFom4IFRSV2eAVv"
                },
            }

        else:
            raise HTTPError(code=404, msg=f"Unsupported user role {user_role}")

        response = quicksight.generate_embed_url_for_registered_user(
            AllowedDomains=[f"*.{settings.LMS_BASE}"],
            AwsAccountId=settings.PANORAMA_AWS_ACCOUNT_ID,
            SessionLifetimeInMinutes=123,
            UserArn=quicksight_arn,
            ExperienceConfiguration=experience_config
        )
        dashboard['url'] = response['EmbedUrl']

    return dashboards_of_user


class GetDashboardEmbedUrl(APIView):
    """
    get dashboard embed url class
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        get dashboard embed url function
        """

        try:
            dashboards_of_user = get_quicksight_dashboards(request.user)
        except HTTPError as e:
            return Response({
                'statusCode': e.code,
                'body': e.reason
            })

        return Response({
            'statusCode': 200,
            'body': dashboards_of_user
        })


class GetUserAccess(APIView):
    """
    get user access class
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        return Response({
            'statusCode': 200,
            'body': has_access_to_panorama(request.user)
        })


class GetUserRole(APIView):
    """
    get user role class
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):

        return Response({
            'statusCode': 200,
            'body': get_user_role(request.user),
        })

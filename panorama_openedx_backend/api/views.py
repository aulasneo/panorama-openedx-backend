"""
panorama_openedx_backend Django application views.
"""

import boto3
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from panorama_openedx_backend.utils import get_user_arn, get_user_dashboards, get_user_role, has_access_to_panorama


class GetDashboardEmbedUrl(APIView):
    """
    get dashboard embed url class
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        get dashboard embed url function
        """
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

        quicksight = session.client(
            "quicksight",
            region_name=settings.PANORAMA_REGION,
        )

        user = request.user

        # user_meta = json.loads(user.profile.meta)

        # CHECKING IF USER HAS A ARN SET
        quicksightARN = get_user_arn(user)
        if not quicksightARN:
            raise ValueError('Error 403 - Forbidden')

        # CHECKING IF USER HAS A DASHBOARD TYPE SET
        dashboards_of_user = get_user_dashboards(user)
        if not dashboards_of_user:
            raise ValueError('Error 404 - Dashboard not assigned')

        # CHECKING IF USER HAS A ROLE SET
        user_role = get_user_role(user)
        if not user_role:
            raise ValueError('Error 404 - User role not assigned')

        dashboard_function = request.GET.get("dashboard_function")

        for dashboard in dashboards_of_user:

            # SETTING EXPERIENCE CONFIG ACCORDING TO USER ROLE
            if dashboard_function == "READER":
                experience_config = {
                    'Dashboard': {
                        'InitialDashboardId': dashboard['id'],
                    }
                }

            if dashboard_function == "AUTHOR":
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

            if dashboard_function == "AI_AUTHOR":
                experience_config = {
                    'QSearchBar': {
                        'InitialTopicId': "CVomHyE9Wf06YnPHcaFom4IFRSV2eAVv"
                    },
                }

            response = quicksight.generate_embed_url_for_registered_user(
                AllowedDomains=[f"*.{settings.LMS_BASE}"],
                AwsAccountId=settings.PANORAMA_AWS_ACCOUNT_ID,
                SessionLifetimeInMinutes=123,
                UserArn=quicksightARN,
                ExperienceConfiguration=experience_config
            )
            dashboard['url'] = response['EmbedUrl']

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

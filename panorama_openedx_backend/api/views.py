from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import json
import boto3
from panorama_openedx_backend.utils import has_access_to_panorama, get_user_dashboards, get_user_arn, get_user_role

class GetDashboardEmbedUrl(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

        quicksight = session.client(
            "quicksight",
            region_name=settings.PANORAMA_REGION,
        )

        user = request.user

        user_meta = json.loads(user.profile.meta)

        quicksightARN = get_user_arn(user)

        # CHECKING IF USER HAS A ARN SET
        if not quicksightARN:
            raise ValueError('Error 403 - Forbidden')
        
        dashboards_of_user = get_user_dashboards(user)

        # CHECKING IF USER HAS A DASHBOARD TYPE SET
        if not dashboards_of_user:
            raise ValueError('Error 404 - Dashboard not assigned')

        all_dashboards = settings.PANORAMA_DASHBOARD_TYPES

        for dashboard in dashboards_of_user:
            response = quicksight.generate_embed_url_for_registered_user(
                AwsAccountId=settings.PANORAMA_AWS_ACCOUNT_ID,
                SessionLifetimeInMinutes=123,
                UserArn=quicksightARN,
                ExperienceConfiguration={
                    'Dashboard': {
                        'InitialDashboardId': dashboard['id'],
                    }
                }
            )
            dashboard['url'] = response['EmbedUrl']

        return Response({
            'statusCode': 200,
            'body': dashboards_of_user
        })


class GetUserAccess(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):

        return Response({
            'statusCode': 200,
            'body': has_access_to_panorama(request.user)
        })
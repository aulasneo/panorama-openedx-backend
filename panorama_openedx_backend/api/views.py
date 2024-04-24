from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import json
import boto3

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


        # CHECKING IF USER HAS AN ARN SET
        if user_meta.get("panorama_user_arn"):
            quicksightARN = user_meta.get("panorama_user_arn")
        else:
            raise ValueError('Error 403 - Forbidden')
        
        # CHECKING IF USER HAS A DASHBOARD TYPE SET
        if user_meta.get("dashboard_type"):
            dashboard_type_of_user = user_meta.get("dashboard_type")
        else:
            raise ValueError('Error 404 - Dashboard not assigned')

        all_dashboards = settings.PANORAMA_DASHBOARD_TYPES

        for dashboard in all_dashboards[dashboard_type_of_user]:
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
            'body': all_dashboards[dashboard_type_of_user]
        })

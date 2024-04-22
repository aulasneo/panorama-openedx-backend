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

        # basic_dashboard_id
        enrollments_dashboard_id = "781857d0-dc98-47f7-bbaf-153c0a252e78"
        grading_dashboard_id = "8f8cfbe8-62d7-4af2-8c3f-0b7871a77078"
        user_activity_dashboard_id = "67adb477-ec5d-4dad-b506-85a7c91b9095"
        engagement_dashboard_id = "d030623c-2fe2-4095-80ce-8ec819c70ff1"

        dashboardTypes = {
            "basic": [
                {
                    "name": "enrollments",
                    "displayName": "Enrollments",
                    "id": enrollments_dashboard_id,
                    "url": ""
                },
                {
                    "name": "engagement",
                    "displayName": "Engagement",
                    "id": engagement_dashboard_id,
                    "url": ""
                },
                {
                    "name": "user activity",
                    "displayName": "User Activity",
                    "id": user_activity_dashboard_id,
                    "url": ""
                },
                {
                    "name": "grading",
                    "displayName": "Grading",
                    "id": grading_dashboard_id,
                    "url": ""
                }
            ]
        }

        quicksight = session.client(
            "quicksight",
            region_name='us-west-2',
        )

        user = request.user

        for dashboard in dashboardTypes["basic"]:
            response = quicksight.generate_embed_url_for_registered_user(
                AwsAccountId='212507341974',
                SessionLifetimeInMinutes=123,
                UserArn='arn:aws:quicksight:us-west-2:212507341974:user/default/andres',
                ExperienceConfiguration={
                    'Dashboard': {
                        'InitialDashboardId': dashboard['id'],
                    }
                }
            )
            dashboard['url'] = response['EmbedUrl']

        data = {
            'embed_url': user.profile.meta,
            'email': user.email,
        }

        return Response({
            'statusCode': 200,
            'body': dashboardTypes["basic"]
        })

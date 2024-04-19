from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class GetDashboardEmbedUrl(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):

        user = request.user

        data = {
            'embed_url': 'Hola Panorama!!',
            'email': user.email,
        }

        return Response(data)

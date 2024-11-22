from rest_framework.views import APIView
from rest_framework.response import Response

class HolaAPIView(APIView):
    def get(self, request):
        return Response({"mensaje": "Hola"})
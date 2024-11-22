from rest_framework.views import APIView
from rest_framework.response import Response

class HolaAPIView(APIView):
    def get(self, request):
        return Response({"mensaje": "Hola"})

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

class MiVista(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"mensaje": "Acceso permitido para todos"})

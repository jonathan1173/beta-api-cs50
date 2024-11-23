# access/views.py
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import ListAPIView
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated

class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'El nombre de usuario ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)

        user = User(
            username=username,
            email=email,
            password=make_password(password)
        )
        user.save()
        return Response({'message': 'Usuario registrado exitosamente'}, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_401_UNAUTHORIZED)


class TopUsersAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.order_by('-points')[:20]
    serializer_class = UserSerializer

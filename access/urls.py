from django.urls import path
from .views import UserRegisterView, UserLoginView ,TopUsersAPIView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('top-users/', TopUsersAPIView.as_view(), name='top-users'),
]

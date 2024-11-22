from django.urls import path
from .views import HolaAPIView

urlpatterns = [
    path('hola/', HolaAPIView.as_view(), name='hola'),
]
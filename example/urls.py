from django.urls import path
from .views import HolaAPIView,  MiVista

urlpatterns = [
    path('hola/', HolaAPIView.as_view(), name='hola'),
    path('hola/', MiVista.as_view(), name='hola'),
]
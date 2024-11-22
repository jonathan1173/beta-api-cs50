from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('example.urls')),
    path('beta/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('beta/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('beta/access/',include('access.urls')),    
    path('beta/challenges/',include('challenges.urls')),    
]

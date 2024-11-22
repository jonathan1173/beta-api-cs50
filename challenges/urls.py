from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChallengeViewSet, LikeDislikeFavoriteView, FilterView

router = DefaultRouter()
router.register(r'challenges', ChallengeViewSet, basename='challenge')

urlpatterns = [
    path('', include(router.urls)),
    path('challenges/<int:challenge_id>/action/<str:action>/', LikeDislikeFavoriteView.as_view(), name='challenge-action'),
    path('filters/', FilterView.as_view(), name='filters'),
]

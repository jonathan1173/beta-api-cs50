from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChallengeViewSet, LikeDislikeFavoriteView, FilterView ,CodeExecutionView ,CodeTestView, SaveSolutionAPIView

router = DefaultRouter()
router.register(r'challenges', ChallengeViewSet, basename='challenge')

urlpatterns = [
    path('', include(router.urls)),
    path('challenges/<int:challenge_id>/action/<str:action>/', LikeDislikeFavoriteView.as_view(), name='challenge-action'),
    path('filters/', FilterView.as_view(), name='filters'),
    path('execute/', CodeExecutionView.as_view(), name='code-execution'),
    path("code-test/", CodeTestView.as_view(), name="code-test"),
    path('challenges/<int:challenge_id>/save-solution/', SaveSolutionAPIView.as_view(), name='save_solution'),
]

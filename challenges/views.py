from rest_framework import generics, viewsets, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Challenge, UserChallenge, Category, Lenguage, Difficulty
from .serializers import (
    ChallengeSerializer, UserChallengeSerializer, CategorySerializer, LanguageSerializer, DifficultySerializer
)


class ChallengePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class FilterView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        languages = Lenguage.objects.all()
        difficulties = Difficulty.objects.all()
        user = request.user

        favorite_challenges = Challenge.objects.filter(
            user_challenges__user=user, user_challenges__favorited=True
        )
        challenges_by_likes = Challenge.objects.all().order_by('-likes_count')

        response_data = {
            'filters': {
                'categories': CategorySerializer(categories, many=True).data,
                'languages': LanguageSerializer(languages, many=True).data,
                'difficulties': DifficultySerializer(difficulties, many=True).data,
            },
            'favorite_challenges': ChallengeSerializer(favorite_challenges, many=True).data,
            'challenges_by_likes': ChallengeSerializer(challenges_by_likes, many=True).data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ChallengeViewSet(viewsets.ModelViewSet):
    queryset = Challenge.objects.all().order_by('id')
    serializer_class = ChallengeSerializer
    pagination_class = ChallengePagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user 
        # Parámetros de consulta
        params = self.request.query_params 
        
        # Filtrar por categoría
        category_name = params.get('category')
        if category_name:
            queryset = queryset.filter(categories__name__iexact=category_name)
        
        # Filtrar por dificultad
        difficulty_name = params.get('difficulty')
        if difficulty_name:
            queryset = queryset.filter(difficulty__grado__iexact=difficulty_name)
        
        # Filtrar por idioma
        language_name = params.get('language')
        if language_name:
            queryset = queryset.filter(language__name__iexact=language_name)
        
        # Filtrar favoritos
        if params.get('favorites') == 'true':
            queryset = queryset.filter(user_challenges__user=user, user_challenges__favorited=True)
        
        # Ordenar por likes
        if params.get('sort_by_likes') == 'true':
            queryset = queryset.order_by('-likes_count')

        return queryset.distinct()


class LikeDislikeFavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, challenge_id, action):
        challenge = Challenge.objects.filter(id=challenge_id).first()
        if not challenge:
            return Response({"error": "Challenge not found"}, status=status.HTTP_404_NOT_FOUND)

        user_challenge, created = UserChallenge.objects.get_or_create(user=request.user, challenge=challenge)

        action_map = {
            'like': ('liked', 'disliked'),
            'dislike': ('disliked', 'liked'),
            'favorite': ('favorited', None)
        }

        if action in action_map:
            if action == 'favorite':
                user_challenge.favorited = not user_challenge.favorited
            else:
                setattr(user_challenge, action_map[action][0], not getattr(user_challenge, action_map[action][0]))
                if action_map[action][1]:
                    setattr(user_challenge, action_map[action][1], False)

            user_challenge.save()
            challenge.update_likes_dislikes_count()

            return Response({
                "user_liked": user_challenge.liked,
                "user_disliked": user_challenge.disliked,
                "user_favorited": user_challenge.favorited,
                "likes_count": challenge.likes_count,
                "dislikes_count": challenge.dislikes_count
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)



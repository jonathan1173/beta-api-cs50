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



import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CodeExecutionSerializer

class CodeExecutionView(APIView):
    def post(self, request):
        serializer = CodeExecutionSerializer(data=request.data)
        if serializer.is_valid():
            language = serializer.validated_data['language']
            code = serializer.validated_data['code']

            default_versions = {
                "python": "*",
                "c": "*",
                "csharp": "*",
                "java": "*",
            }

            # Verificar que el lenguaje sea soportado
            if language not in default_versions:
                return Response(
                    {"error": f"El lenguaje '{language}' no está soportado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Obtener la versión predeterminada del lenguaje
            version = default_versions[language]

            # Crear el payload para la API de Piston
            piston_url = "https://emkc.org/api/v2/piston/execute"
            payload = {
                "language": language,
                "version": version,
                "files": [
                    {
                        "name": f"main.{language}",  # Nombrar el archivo según el lenguaje
                        "content": code,
                          "stdin": "5\n6"
                    }
                ]
            }

            try:
                # Enviar la solicitud a la API de Piston
                response = requests.post(piston_url, json=payload)
                response_data = response.json()

                # Retornar la respuesta de Piston al cliente
                return Response(response_data, status=response.status_code)
            except requests.RequestException:
                return Response(
                    {"error": "Error al conectar con Piston API"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Respuesta de error en caso de datos inválidos
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Challenge, User
from .serializers import CodeTestSerializer
import requests

class CodeTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CodeTestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        challenge = Challenge.objects.get(id=validated_data["challenge_id"])
        solution = validated_data["solution"]

        # Combinar código de solución y test
        code_to_execute = f"{solution}\n\n{challenge.test}"
        print("Code to execute:")
        print(code_to_execute)

        # Ajustar el payload para cumplir con la API de Piston
        payload = {
            "language": challenge.language.name.lower(),
            "version": "*",
            "files": [
                {
                    "name": "main.py",
                    "content": code_to_execute
                }
            ]
        }

        # Llamar a la API de Piston
        response = requests.post(
            url="https://emkc.org/api/v2/piston/execute",
            json=payload,
        )

        if response.status_code != 200:
            print("Piston API Error:", response.json())
            return Response({"error": "Error evaluating code"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        execution_result = response.json()
        stdout = execution_result["run"].get("stdout", "")
        stderr = execution_result["run"].get("stderr", "")
        print("Execution result stdout:", stdout)
        print("Execution result stderr:", stderr)

        # Analizar resultados
        total_tests = challenge.test.count("assert")  # Número de tests definidos
        successful_tests = stdout.count("passed")  # Contar "passed" en la salida

        # Obtener nivel de dificultad
        difficulty = challenge.difficulty  # Accede al objeto relacionado Difficulty
        base_points = int(difficulty.grado) * 10  # Calcula los puntos base
        points_per_test = base_points / total_tests if total_tests > 0 else 0  # Puntos por cada test

        # Calcular puntos según los tests exitosos
        points_awarded = int(successful_tests * points_per_test)

        # Actualizar puntos del usuario
        user = request.user
        user.points += points_awarded
        user.save()

        # Mensaje de resultado
        if successful_tests == total_tests:
            message = "All tests passed successfully!"
        else:
            message = f"Passed {successful_tests}/{total_tests} tests"

        return Response({
            "message": "Code evaluated successfully",
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_percentage": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            "points_awarded": points_awarded,
            "output": message,
        }, status=status.HTTP_200_OK if successful_tests > 0 else status.HTTP_400_BAD_REQUEST)

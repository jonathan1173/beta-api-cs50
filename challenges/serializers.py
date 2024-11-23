from rest_framework import serializers
from .models import Challenge, UserChallenge, Category, Lenguage, Difficulty


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lenguage
        fields = ['id', 'name']


class DifficultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Difficulty
        fields = ['id', 'grado']


class ChallengeSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    dislikes_count = serializers.IntegerField(read_only=True)
    user_liked = serializers.SerializerMethodField()
    user_disliked = serializers.SerializerMethodField()
    user_favorited = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True)
    language = serializers.CharField(source='language.name')

    class Meta:
        model = Challenge
        fields = [
            'id', 'title', 'description', 'difficulty', 'categories', 'language',
            'likes_count', 'dislikes_count', 'user_liked', 'user_disliked', 'user_favorited', 'solution', 'test'
        ]
        extra_kwargs = {
            # Permite que el campo solution sea opcional en una actualización
            'solution': {'required': False},  
            # Permite que el campo test sea opcional
            'test': {'required': False}, 
        }

    def get_user_liked(self, obj):
        request = self.context.get('request')
        return (
            UserChallenge.objects.filter(user=request.user, challenge=obj, liked=True).exists()
            if request and request.user.is_authenticated
            else False
        )

    def get_user_disliked(self, obj):
        request = self.context.get('request')
        return (
            UserChallenge.objects.filter(user=request.user, challenge=obj, disliked=True).exists()
            if request and request.user.is_authenticated
            else False
        )

    def get_user_favorited(self, obj):
        request = self.context.get('request')
        return (
            UserChallenge.objects.filter(user=request.user, challenge=obj, favorited=True).exists()
            if request and request.user.is_authenticated
            else False
        )

    def update(self, instance, validated_data):
        # Actualiza los campos según el validated_data
        if 'solution' in validated_data:
            instance.solution = validated_data['solution']
        if 'test' in validated_data:
            instance.test = validated_data['test']
        
        instance.save()
        return instance


class UserChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChallenge
        fields = ['id', 'user', 'challenge', 'liked', 'disliked', 'favorited']
        read_only_fields = ['user', 'challenge']

from rest_framework import serializers

class CodeExecutionSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=[
        ('python', 'Python'),
        ('c', 'C'),
        ('csharp', 'C#'),
        ('java', 'Java'),
    ])
    code = serializers.CharField()


from rest_framework import serializers

class CodeExecutionSerializer(serializers.Serializer):
    test = serializers.CharField()
    solution = serializers.CharField()
    language = serializers.ChoiceField(choices=["python", "javascript"])




from rest_framework import serializers
from .models import Challenge


class CodeTestSerializer(serializers.Serializer):
    challenge_id = serializers.IntegerField(required=True)
    solution = serializers.CharField(required=True)

    def validate(self, data):
        # Validar si el desafío existe
        try:
            challenge = Challenge.objects.get(id=data["challenge_id"])
        except Challenge.DoesNotExist:
            raise serializers.ValidationError({"challenge_id": "Challenge not found"})

        # Validar el lenguaje permitido
        if challenge.language.name not in ["python", "javascript"]:
            raise serializers.ValidationError({"language": "Only Python and JavaScript are supported"})

        return data

from django.db import models
from access.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Lenguage(models.Model):  
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Difficulty(models.Model):
    grado = models.CharField(max_length=100)

    def __str__(self):
        return self.grado


class Challenge(models.Model):
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    test = models.TextField(blank=True, null=True)
    solution = models.TextField(blank=True, null=True)
    difficulty = models.ForeignKey(Difficulty, on_delete=models.CASCADE, related_name="challenges")
    categories = models.ManyToManyField(Category, blank=True)
    language = models.ForeignKey(Lenguage, on_delete=models.CASCADE, related_name="challenges")
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} - {self.language}"

    def update_likes_dislikes_count(self):
        self.likes_count = UserChallenge.objects.filter(challenge=self, liked=True).count()
        self.dislikes_count = UserChallenge.objects.filter(challenge=self, disliked=True).count()
        self.save()


class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="user_challenges")
    liked = models.BooleanField(default=False)
    disliked = models.BooleanField(default=False)
    favorited = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"

    def save(self, *args, **kwargs):
        if self.liked and self.disliked:
            raise ValueError("Cannot like and dislike the same challenge.")
        super().save(*args, **kwargs)
        self.challenge.update_likes_dislikes_count()


class ChallengeComment(models.Model):
    user_challenge = models.ForeignKey(UserChallenge, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.user_challenge.user.username} sobre {self.user_challenge.challenge.title}"

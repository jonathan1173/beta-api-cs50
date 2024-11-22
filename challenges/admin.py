from django.contrib import admin
from .models import Challenge, UserChallenge, Category, Lenguage, Difficulty


admin.site.register(Challenge)
admin.site.register(UserChallenge)
admin.site.register(Category)
admin.site.register(Lenguage)
admin.site.register(Difficulty)


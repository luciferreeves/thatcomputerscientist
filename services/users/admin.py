from django.contrib import admin

# Register your models here.
from .models import TokenStore, UserProfile

admin.site.register(UserProfile)
admin.site.register(TokenStore)

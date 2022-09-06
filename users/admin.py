from django.contrib import admin

# Register your models here.
from .models import UserProfile, CaptchaStore

admin.site.register(UserProfile)
admin.site.register(CaptchaStore)

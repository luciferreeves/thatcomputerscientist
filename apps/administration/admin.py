from django.contrib import admin

# Register your models here.
from apps.administration.models import Announcement

admin.site.register(Announcement)

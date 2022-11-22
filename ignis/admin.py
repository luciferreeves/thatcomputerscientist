from django.contrib import admin

# Register your models here.
from .models import Object, ObjectDirectory

admin.site.register(Object)
admin.site.register(ObjectDirectory)
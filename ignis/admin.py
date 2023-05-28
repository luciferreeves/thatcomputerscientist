from django.contrib import admin

# Register your models here.
from .models import CoverImage, PostImage, RepositoryTitle

admin.site.register(PostImage)
admin.site.register(RepositoryTitle)
admin.site.register(CoverImage)

from django.contrib import admin

# Register your models here.
from .models import AnonymousCommentUser, Category, Comment, Post, Tag

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(AnonymousCommentUser)

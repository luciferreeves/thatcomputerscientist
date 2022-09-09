from django.urls import path
from . import views

app_name = 'blog-admin'
urlpatterns = [
    path('users', views.users, name='users'),
    path('posts', views.posts, name='posts'),
    path('comments', views.comments, name='comments'),
    path('categories', views.categories, name='categories'),
    path('tags', views.tags, name='tags'),
    path('new', views.new, name='new'),
]
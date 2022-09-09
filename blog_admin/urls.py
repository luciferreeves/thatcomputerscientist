from django.urls import path
from . import views

app_name = 'blog-admin'
urlpatterns = [
    path('users', views.users, name='users'),
    path('users/new', views.new_user, name='new-user'),
    path('users/<int:user_id>/edit', views.edit_user, name='edit-user'),
    path('posts', views.posts, name='posts'),
    path('comments', views.comments, name='comments'),
    path('categories', views.categories, name='categories'),
    path('tags', views.tags, name='tags'),
    path('new', views.new, name='new'),
    path('search', views.search, name='search'),
]
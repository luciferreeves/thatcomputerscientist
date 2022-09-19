from django.urls import path
from . import views

app_name = 'blog-admin'
urlpatterns = [
    path('users', views.users, name='users'),
    path('users/new', views.new_user, name='new-user'),
    path('users/search', views.users_search, name='users-search'),
    path('users/<int:user_id>/edit', views.edit_user, name='edit-user'),
    path('posts', views.posts, name='posts'),
    path('posts/new', views.new_post, name='new-post'),
    path('posts/search', views.posts_search, name='posts-search'),
    path('comments', views.comments, name='comments'),
    path('categories', views.categories, name='categories'),
    path('tags', views.tags, name='tags'),
    path('new', views.new, name='new'),
]
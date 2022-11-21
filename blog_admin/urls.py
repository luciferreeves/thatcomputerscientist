from django.urls import path
from . import views

app_name = 'blog-admin'
urlpatterns = [
    path('/users', views.users, name='users'),
    path('/users/new', views.new_user, name='new-user'),
    path('/users/search', views.users_search, name='users-search'),
    path('/users/<int:user_id>/edit', views.edit_user, name='edit-user'),
    path('/posts', views.posts, name='posts'),
    path('/posts/new', views.new_post, name='new-post'),
    path('/posts/search', views.posts_search, name='posts-search'),
    path('/posts/<str:slug>/edit', views.edit_post, name='edit-post'),
    path('/posts/<str:slug>/publish', views.publish_post, name='publish-post'),
    path('/posts/<str:slug>/unpublish', views.unpublish_post, name='unpublish-post'),
    path('/comments', views.comments, name='comments'),
    path('/categories', views.categories, name='categories'),
    path('/categories/new', views.new_category, name='new-category'),
    path('/categories/<int:category_id>/edit', views.edit_category, name='edit-category'),
    path('/categories/<int:category_id>/delete', views.edit_category, name='delete-category'),
    path('/tags', views.tags, name='tags'),
    path('/new', views.new, name='new'),
]
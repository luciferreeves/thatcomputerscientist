from django.urls import path

from . import views

app_name = 'blog-admin'
urlpatterns = [
    path('/posts', views.posts, name='posts'),
    path('/postAction.do', views.new_post, name='new-post'),
    path('/posts/search', views.posts_search, name='posts-search'),
    path('/posts/<str:slug>/edit', views.edit_post, name='edit-post'),
    path('/posts/<str:slug>/publish', views.publish_post, name='publish-post'),
    path('/posts/<str:slug>/unpublish', views.unpublish_post, name='unpublish-post'),
    path('/comments', views.comments, name='comments'),
]
from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.home, name='home'),
    path('account', views.account, name='account'),
    path('register', views.register, name='register'),
    path('search', views.search, name='search'),
    path('articles', views.articles, name='articles'),
    path('articles/<str:slug>', views.post, name='post'),
    path('articles/<str:slug>/comment', views.comment, name='comment'),
    path('articles/<str:slug>/edit_comment', views.edit_comment, name='edit_comment'),
    path('articles/<str:slug>/delete_comment/<int:comment_id>', views.delete_comment, name='delete_comment'),
    path('users/~<str:username>', views.user_activity, name='user_activity'),
]

from django.urls import path

from . import views
from .feed import RSSFeed

app_name = 'blog'
urlpatterns = [
    path('', views.home, name='home'),
    path('account', views.account, name='account'),
    path('register', views.register, name='register'),
    path('search', views.search, name='search'),
    path('weblog', views.articles, name='articles'),
    path('weblog/<str:slug>', views.post, name='post'),
    path('weblog/<str:slug>/comment', views.comment, name='comment'),
    path('weblog/<str:slug>/anon_comment', views.anon_comment, name='anon_comment'),
    path('weblog/<str:slug>/edit_comment', views.edit_comment, name='edit_comment'),
    path('weblog/<str:slug>/anon_edit_comment', views.anon_edit_comment, name='anon_edit_comment'),
    path('weblog/<str:slug>/delete_comment/<int:comment_id>', views.delete_comment, name='delete_comment'),
    path('weblog/<str:slug>/anon_delete_comment/<int:comment_id>', views.anon_delete_comment, name='anon_delete_comment'),
    path('archives', views.archives, name='archives'),
    path('archives/<str:date>', views.articles, name='archive_posts'),
    path('categories', views.categories, name='categories'),
    path('categories/<str:cg>', views.articles, name='category_posts'),
    path('tags', views.tags, name='tags'),
    path('tags/<str:tag_slug>', views.tag_posts, name='tag_posts'),
    path('~<str:username>', views.user_activity, name='user_activity'),
    path('policy', views.policy, name='policy'),
    path('socialify', views.socialify, name='socialify'),
    path('rss/', RSSFeed(), name='rss_feed'),
    path('anidata', views.anidata, name='anidata'),
    path('anilist', views.anilist, name='anilist'),
]

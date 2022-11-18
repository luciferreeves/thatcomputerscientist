from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.home, name='home'),
    path('my/', RedirectView.as_view(pattern_name='account', permanent=False)),
    path('account/', RedirectView.as_view(pattern_name='account', permanent=False)),
    path('my/account', views.account, name='account'),
    path('register/', views.register, name='register'),
    path('register/refresh_captcha/', name='refresh_captcha', view=views.refresh_captcha),
    path('post/<str:slug>', views.post, name='post'),
    path('post/<str:slug>/comment', views.comment, name='comment'),
    path('post/<str:slug>/edit_comment', views.edit_comment, name='edit_comment'),
    path('post/<str:slug>/delete_comment/<int:comment_id>', views.delete_comment, name='delete_comment'),
    # path('my/homepage', views.homepage, name='homepage'),
]

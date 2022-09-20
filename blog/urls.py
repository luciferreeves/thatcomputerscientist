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
    # path('my/homepage', views.homepage, name='homepage'),
]

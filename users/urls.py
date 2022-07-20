from multiprocessing.dummy import Namespace
from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
]

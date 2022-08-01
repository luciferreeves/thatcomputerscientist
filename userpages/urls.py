from django.urls import path
from . import views

# Configure the URL patterns for username.*
urlpatterns = [
    # match for username.*
    path('', views.home, name='home'),
]

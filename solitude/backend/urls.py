from django.urls import re_path

from . import views

app_name = 'solitude'

urlpatterns = [
    re_path(r'^.*$', views.home),
]

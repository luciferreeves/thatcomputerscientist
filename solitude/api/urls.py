from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('whoami', views.CurrentUser.as_view(), name='whoami'),
]

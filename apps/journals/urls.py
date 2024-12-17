from django.urls import path

from . import views

app_name = "journal"
urlpatterns = [
    path("<slug:slug>/", views.single_journal, name="single"),
]

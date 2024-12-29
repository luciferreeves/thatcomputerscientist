from django.urls import path

from . import views

app_name = "journal"
urlpatterns = [
    path("", views.journal_of_random_thoughts, name="journal_of_random_thoughts"),
    path("<slug:slug>/", views.single_journal, name="single"),
]

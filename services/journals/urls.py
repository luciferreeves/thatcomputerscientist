from django.urls import path
from services.journals import views

app_name = "journals"

urlpatterns = [
    path("", views.journals, name="journals"),
    path("/new", views.new_journal, name="new"),
    path("/<slug:slug>", views.journal, name="journal"),
]

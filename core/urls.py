from django.urls import path, include
from . import views

app_name = "core"
urlpatterns = [
    path("", views.home, name="home"),
    path("screenshots", views.screenshots, name="screenshots"),
    path("journal", views.journal, name="journal_default"),
    path("journal/<slug:slug>", views.journal, name="journal"),
    path("letters", include("core.letters.urls")),
    path("ignis/<path:path>", views.ignis_wrapper_temp, name="ignis_wrapper"),
]

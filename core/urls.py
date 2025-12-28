from django.urls import path
from . import views

app_name = "core"
urlpatterns = [
    path("", views.home, name="home"),
    path("ignis/<path:path>", views.ignis_wrapper_temp, name="ignis_wrapper"),
]

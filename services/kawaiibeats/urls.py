from django.urls import path
from services.kawaiibeats import views

app_name = "kawaiibeats"

urlpatterns = [
    path("", views.random_song, name="random_song"),
]

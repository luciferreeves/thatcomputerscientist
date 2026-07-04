from django.urls import path

from api.kawaiibeats import random_song

app_name = "kawaiibeats"

urlpatterns = [
    path("random", random_song.random_song, name="random_song"),
]

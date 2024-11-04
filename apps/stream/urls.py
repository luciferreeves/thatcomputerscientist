from django.urls import path

from . import views

app_name = "stream"
urlpatterns = [
    path("random-song", views.random_song, name="random_song"),
    path("song/<str:song_id>", views.stream_song, name="stream_song"),
]

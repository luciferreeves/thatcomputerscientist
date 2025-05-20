from django.urls import path
from administration.song_streams import views as song_streams_views

app_name = "administration"
urlpatterns = [
    path("song_streams/", song_streams_views.song_streams, name="song_streams"),
]

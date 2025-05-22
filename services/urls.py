from django.urls import path

from services.pamphlet import views as pamphlet
from services.kawaiibeats import views as kawaiibeats

app_name = "services"
urlpatterns = [
    path("pamphlet", pamphlet.pamphlet, name="pamphlet"),
    path("kawaiibeats", kawaiibeats.random_song, name="random_song"),
]

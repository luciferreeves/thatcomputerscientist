from django.urls import path
from administration.annoucements import views as announcements
from administration.emojis import views as emojis
from administration.kawaiibeats import views as kawaiibeats

app_name = "administration"
urlpatterns = [
    path("/announcements", announcements.home, name="announcements"),
    path("/emojis", emojis.home, name="emojis"),
    path("/kawaiibeats", kawaiibeats.home, name="kawaiibeats"),
]

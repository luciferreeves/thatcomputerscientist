from django.urls import path
from administration.kawaiibeats import views as kawaiibeats
from administration.annoucements import views as announcements

app_name = "administration"
urlpatterns = [
    path("/kawaiibeats", kawaiibeats.home, name="kawaiibeats"),
    path("/announcements", announcements.home, name="announcements"),
]

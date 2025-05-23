from django.urls import path
from administration.kawaiibeats import views as kawaiibeats

app_name = "administration"
urlpatterns = [
    path("/kawaiibeats", kawaiibeats.home, name="kawaiibeats"),
]

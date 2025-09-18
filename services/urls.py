from django.urls import path, include

from services.pamphlet import views as pamphlet_views
from services.kawaiibeats import views as kawaiibeats_views

app_name = "services"
urlpatterns = [
    path("/journals", include("services.journals.urls")),
    path("/kawaiibeats", kawaiibeats_views.random_song, name="kawaiibeats_random_song"),
    path("/pamphlet", pamphlet_views.pamphlet, name="pamphlet"),
]

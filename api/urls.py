from django.urls import path, include

app_name = "api"

urlpatterns = [
    path("kawaiibeats/", include("api.kawaiibeats.urls", namespace="kawaiibeats")),
    path("letters/", include("api.letters.urls", namespace="letters")),
]

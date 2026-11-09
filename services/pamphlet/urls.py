from django.urls import path
from services.pamphlet import views

app_name = "pamphlet"

urlpatterns = [
    path("", views.pamphlet, name="pamphlet"),
]

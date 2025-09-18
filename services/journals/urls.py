from django.urls import path
from services.journals import views

app_name = "journals"

urlpatterns = [
    path("", views.journals, name="journals"),
]

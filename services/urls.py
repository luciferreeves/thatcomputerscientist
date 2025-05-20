from django.urls import path

from services.pamphlet import views as pamphlet_views

app_name = "services"
urlpatterns = [
    path("pamphlet", pamphlet_views.pamphlet, name="pamphlet"),
]

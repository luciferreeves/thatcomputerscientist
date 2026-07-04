from django.urls import path, include

app_name = "services"
urlpatterns = [
    path("/journals", include("services.journals.urls")),
    path("/pamphlet", include("services.pamphlet.urls")),
]

from django.urls import path

from . import views

app_name = "pamphlet"
urlpatterns = [
    path("", views.new_pamphlet, name="new_pamphlet"),
]

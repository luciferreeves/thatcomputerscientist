from django.urls import path
from core.letters import views

app_name = "letters"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("/compose", views.compose, name="compose"),
    path("/compose/<str:username>", views.compose, name="compose_to"),
    path("/@<str:username>", views.conversation, name="conversation"),
    path("/@<str:username>/older", views.conversation_older, name="conversation_older"),
]

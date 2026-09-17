from django.urls import path

from sockets.letters.consumers import ConversationConsumer

websocket_urlpatterns = [
    path("ws/letters/<str:username>/", ConversationConsumer.as_asgi()),
]

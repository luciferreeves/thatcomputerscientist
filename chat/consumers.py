import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .chat_cache import handle_connect, handle_disconnect, handle_alone_user, discard_user_messages
from .skippy import invokeMFSkippy

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = "chat"
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()
        handle_connect()
    
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
        handle_disconnect()
        discard_user_messages(user_identifier=self.channel_name)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat", "message": message, "username": username}
        )
        is_alone_user = handle_alone_user()
        if is_alone_user:
            skippy_message = invokeMFSkippy(message=message, identifier=self.channel_name)
            if skippy_message:
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name, {"type": "chat", "message": skippy_message, "username": "Skippy"}
                )

    # Receive message from room group
    def chat(self, event):
        message = event["message"]
        username = event["username"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message, "username": username}))


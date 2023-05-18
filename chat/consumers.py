import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .chat_cache import handle_connect, handle_disconnect, handle_alone_user, discard_user_messages
from .ai import invokeMFSkippy

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'chat'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        handle_connect()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        handle_disconnect()
        discard_user_messages(user_identifier=self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat", "message": message, "username": username}
        )
        is_alone_user = handle_alone_user()
        if is_alone_user:
            bot_response = invokeMFSkippy(message=message, identifier=self.channel_name)
            if bot_response:
                await self.channel_layer.group_send(
                    self.room_group_name, {"type": "chat", "message": bot_response, "username": "Skippy"}
                )
        else:
            discard_user_messages(user_identifier=self.channel_name)

    # Receive message from room group
    async def chat(self, event):
        message = event["message"]
        username = event["username"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "username": username}))


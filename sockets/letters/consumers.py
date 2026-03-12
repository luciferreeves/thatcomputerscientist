from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from core.letters.functions import (
    find_user_by_username,
    get_conversation_by_users,
    get_letter_attachments,
    has_pending_attachments,
    mark_letters_read,
    send_letter,
)


class ConversationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        self.other_username = self.scope["url_route"]["kwargs"]["username"]
        self.conversation = await self._get_conversation()

        if not self.conversation:
            await self.close()
            return

        self.room_group = f"letters_{self.conversation.pk}"

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group"):
            await self.channel_layer.group_discard(
                self.room_group, self.channel_name
            )

    async def receive_json(self, content):
        msg_type = content.get("type")

        if msg_type == "letter.send":
            await self._handle_send(content)
        elif msg_type == "letter.read":
            await self._handle_read()

    async def _handle_send(self, content):
        text = content.get("content", "").strip()
        has_attachments = await database_sync_to_async(has_pending_attachments)(
            self.user, self.conversation
        )

        if not text and not has_attachments:
            return

        letter = await database_sync_to_async(send_letter)(
            self.user, self.conversation, text
        )
        if not letter[0]:
            return

        letter = letter[1]
        attachments = await database_sync_to_async(get_letter_attachments)(letter)

        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "letter.new",
                "letter_id": letter.pk,
                "sender": self.user.username,
                "content": letter.content,
                "created_at": letter.created_at.isoformat(),
                "attachments": attachments,
            },
        )

    async def _handle_read(self):
        await database_sync_to_async(mark_letters_read)(
            self.user, self.conversation
        )
        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "letter.read_receipt",
                "reader": self.user.username,
            },
        )

    # --- group message handlers ---

    async def letter_new(self, event):
        await self.send_json(
            {
                "type": "letter.new",
                "letter_id": event["letter_id"],
                "sender": event["sender"],
                "content": event["content"],
                "created_at": event["created_at"],
                "attachments": event.get("attachments", []),
            }
        )

    async def letter_read_receipt(self, event):
        await self.send_json(
            {
                "type": "letter.read_receipt",
                "reader": event["reader"],
            }
        )

    # --- db helpers ---

    @database_sync_to_async
    def _get_conversation(self):
        success, result = find_user_by_username(self.other_username)
        if not success:
            return None

        return get_conversation_by_users(self.user, result)

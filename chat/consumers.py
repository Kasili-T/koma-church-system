import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message

# Keep track of online users per room
online_users = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        self.user = self.scope["user"]

        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Add user to online list
        if self.room_id not in online_users:
            online_users[self.room_id] = set()
        online_users[self.room_id].add(self.user.username)

        # Broadcast updated presence
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "presence",
                "users": list(online_users[self.room_id]),
            }
        )

    async def disconnect(self, close_code):
        # Remove user from online list
        if self.room_id in online_users:
            online_users[self.room_id].discard(self.user.username)

            # Broadcast updated presence
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "presence",
                    "users": list(online_users[self.room_id]),
                }
            )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type")

        if msg_type == "chat":
            message = data["message"]

            # Save message to DB
            await self.save_message(self.room_id, self.user, message)

            # Broadcast message
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": self.user.username,
                }
            )

        elif msg_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_indicator",
                    "username": self.user.username,
                    "is_typing": data["is_typing"],
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "message": event["message"],
            "username": event["username"],
        }))

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "username": event["username"],
            "is_typing": event["is_typing"],
        }))

    async def presence(self, event):
        await self.send(text_data=json.dumps({
            "type": "presence",
            "users": event["users"],
        }))

    @database_sync_to_async
    def save_message(self, room_id, user, message):
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(room=room, sender=user, content=message)

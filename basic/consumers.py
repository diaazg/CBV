# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message, Room
from django.utils import timezone
from asgiref.sync import sync_to_async

class DirectChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'direct_chat_{self.room_name}'

        room_exists = await self.room_exists(self.room_name)
        if room_exists:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            # Create a new room
            user_ids = self.room_name.split('_')
            if len(user_ids) == 2:
                user1_id, user2_id = user_ids
                user1 = await sync_to_async(User.objects.get)(id=user1_id)
                user2 = await sync_to_async(User.objects.get)(id=user2_id)

                # Create the room
                await sync_to_async(Room.objects.create)(name=self.room_name)

                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                await self.accept()
            else:
                await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']
        receiver_id = text_data_json['receiver_id']

        sender = await sync_to_async(User.objects.get)(id=sender_id)
        receiver = await sync_to_async(User.objects.get)(id=receiver_id)

        Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=message,
            date_time=timezone.now()
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,
                'receiver': receiver.username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'receiver': receiver
        }))

    @sync_to_async
    def room_exists(self, room_name):
        return Room.objects.filter(name=room_name).exists()

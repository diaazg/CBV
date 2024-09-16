# consumers.py

from datetime import datetime
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message, Room
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist

class DirectChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'direct_chat_{self.room_name}'

        room_exists_obj = await self.room_exists(self.room_name)
        exist = room_exists_obj['exist']
        room_name = room_exists_obj['value']
        if exist:
            self.room_group_name = f'direct_chat_{room_name}'
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
        action = text_data_json.get('action', 'send')

        
        if action == 'send':
            await self.handle_send_message(text_data_json)
        elif action == 'delete':
            await self.handle_delete_message(text_data_json)

    async def handle_send_message(self, text_data_json):
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']
        receiver_id = text_data_json['receiver_id']
        print(message)
    
        sender = await sync_to_async(User.objects.get)(id=sender_id)
        receiver = await sync_to_async(User.objects.get)(id=receiver_id)

        created_message = await sync_to_async(Message.objects.create)(
            sender=sender,
            receiver=receiver,
            content=message,
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': created_message.content,
                'sender': sender.id,
                'receiver': receiver.id,
                'message_id': created_message.id,
                'date_time': created_message.date_time
            }
        )

    async def handle_delete_message(self, text_data_json):
        message_id = text_data_json['message_id']
        try:
            await self.delete_message(message_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message_deleted',
                    'message_id': message_id
                }
            )
        except ObjectDoesNotExist:
            
            pass

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']
        message_id = event.get('message_id')
        date_time = event['date_time']
        if isinstance(date_time, datetime):
         date_time = date_time.isoformat() 
        
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'receiver': receiver,
            'message_id': message_id,
            'date_time':date_time
        }))

    async def chat_message_deleted(self, event):
        message_id = event['message_id']

        await self.send(text_data=json.dumps({
            'action': 'delete',
            'message_id': message_id
        }))

    @sync_to_async
    def room_exists(self, room_name):
        print('--------------------------')
        print( self.room_name)
        print('--------------------------')
        if Room.objects.filter(name=room_name).exists():
            
            return {'exist':True,'value':room_name}
        else:
            user_ids = self.room_name.split('_')
            if len(user_ids) == 2:
                user1_id, user2_id = user_ids
                new_name = f'{user2_id}_{user1_id}'
                exist = Room.objects.filter(name=new_name).exists()
                
                return  {'exist':exist,'value':new_name}
                 
            else:
                print('hhhhhhhhhhhhhhhhhhhhhhhhhhh')
                return  {'exist':False,'value':''}

    @database_sync_to_async
    def delete_message(self, message_id):
        message = Message.objects.get(id=message_id)
        message.delete()
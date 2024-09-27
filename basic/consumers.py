# consumers.py

from datetime import datetime
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from .models import Message, Room
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
import base64
from django.core.files.base import ContentFile
from .services import *
from django.conf import settings


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

        elif action == 'start_call':
            await self.handle_start_video_call(text_data_json) 

        elif action=='image':
            await self.handle_send_image(text_data)

        else:
          await self.handle_audio_message(text_data)

## Text message

    async def handle_send_message(self, text_data_json):
        
        sender_id = text_data_json['sender_id']
        receiver_id = text_data_json['receiver_id']
        text_content = text_data_json["message"]
        message_type = 'text'

        
    
        sender = await sync_to_async(User.objects.get)(id=sender_id)
        receiver = await sync_to_async(User.objects.get)(id=receiver_id)

        created_message = await sync_to_async(Message.objects.create)(
            sender=sender,
            receiver=receiver,
            text_content=text_content,
            message_type=message_type
        )
        
       

        ## update last connection
        
        friendship = await sync_to_async(Friend.objects.get)(
            Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
        )
        friendship.last_connection =  timezone.now()
        await sync_to_async(friendship.save)()
        
        ## update user state 

        user_info = await sync_to_async(UserInfo.objects.get)(user=sender)
        user_info.last_date_connected = timezone.now()
        user_state = user_info.last_date_connected
        await sync_to_async(user_info.save)()



        

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'text_content': created_message.text_content,
                'audio_file':'',
                'image_file':'',
                'sender': sender.id,
                'receiver': receiver.id,
                'message_id': created_message.id,
                'date_time': created_message.date_time,
                'user_state':user_state
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
        state = event['user_state']
        message = event['text_content']
        sender = event['sender']
        receiver = event['receiver']
        message_id = event.get('message_id')
        date_time = event['date_time']
        if isinstance(date_time, datetime):
         date_time = date_time.isoformat() 
        if isinstance(state, datetime):
         state = state.isoformat() 

        
        await self.send(text_data=json.dumps({
            'type':'text',
            'text_content': message,
            'audio_file':'',
            'image_file':'',
            'sender': sender,
            'receiver': receiver,
            'message_id': message_id,
            'date_time':date_time,
            'user_state':state
        }))

    async def chat_message_deleted(self, event):
        message_id = event['message_id']

        await self.send(text_data=json.dumps({
            'action': 'delete',
            'message_id': message_id
        }))
     

## Audio message


    async def handle_audio_message(self, data):
        data = json.loads(data)
        base64_audio = data['message']
        sender_id = data['sender_id']
        receiver_id = data['receiver_id']

        


        # Save the audio file and create a message record
        sender = await sync_to_async(User.objects.get)(id=sender_id)
        receiver = await sync_to_async(User.objects.get)(id=receiver_id)


        empty_message = await sync_to_async(Message.objects.create)(
            sender=sender,
            receiver=receiver,
            message_type='audio'
        )




        message_id = empty_message.id

        
        file_name = f'{message_id}.wav'
        audio_file = base64.b64decode(base64_audio)
        file = ContentFile(audio_file, file_name)
        empty_message.audio_file = file
        await sync_to_async(empty_message.save)()

        
        ## update last connection

        friendship = await sync_to_async(Friend.objects.get)(
            Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
        )
        friendship.last_connection =  timezone.now()
        await sync_to_async(friendship.save)()
        
                ## update user state 

        user_info = await sync_to_async(UserInfo.objects.get)(user=sender)
        user_info.last_date_connected = timezone.now()
        user_state = user_info.last_date_connected
        await sync_to_async(user_info.save)()
        
        



        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'audio_message',
                'audio_file': empty_message.audio_file.url,
                'image_file':'',
                'text_content':'',
                'sender': sender_id,
                'receiver': receiver_id,
                'message_id': message_id,
                'date_time': empty_message.date_time.isoformat(),
                'user_state':user_state.isoformat()
            }
        )
  
  
    async def audio_message(self, event):
        # Send the audio message to WebSocket
        
        await self.send(text_data=json.dumps({
            'type': 'audio',
            'audio_file': event['audio_file'],
            'text_content':'',
            'image_file':'',
            'sender': event['sender'],
            'receiver': event['receiver'],
            'message_id': event['message_id'],
            'date_time': event['date_time'],
            'user_state':event['user_state']
        }))        


## Image message

    async def handle_send_image(self,data):
        
        data = json.loads(data)
        base64_image = data['message']
        sender_id = data['sender_id']
        receiver_id = data['receiver_id']

        print(base64_image)
        print("i---------------------------------")
        
        sender = await sync_to_async(User.objects.get)(id=sender_id)
        receiver = await sync_to_async(User.objects.get)(id=receiver_id)

        empty_message = await sync_to_async(Message.objects.create)(
            sender=sender,
            receiver=receiver,
            message_type='image'
        )

        message_id = empty_message.id

        file_name = f'{message_id}.jpg'
        image_file = base64.b64decode(base64_image)
        file = ContentFile(image_file, file_name)
        empty_message.image_file = file
        await sync_to_async(empty_message.save)()

        image_url = f"{settings.MEDIA_URL}{empty_message.image_file}"
        

        ## update last connection

        friendship = await sync_to_async(Friend.objects.get)(
            Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
        )
        friendship.last_connection =  timezone.now()
        await sync_to_async(friendship.save)()
        
        ## update user state 

        user_info = await sync_to_async(UserInfo.objects.get)(user=sender)
        user_info.last_date_connected = timezone.now()
        user_state = user_info.last_date_connected
        await sync_to_async(user_info.save)()


        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'image_message',
                'audio_file': '',
                'text_content':'',
                'image_file':image_url,
                'sender': sender_id,
                'receiver': receiver_id,
                'message_id': message_id,
                'date_time': empty_message.date_time.isoformat(),
                'user_state':user_state.isoformat()
            }
        )
        

    async def image_message(self,event):


        await self.send(text_data=json.dumps({
            'type': 'audio',
            'audio_file': '',
            'text_content':'',
            'image_file':event['image_file'],
            'sender': event['sender'],
            'receiver': event['receiver'],
            'message_id': event['message_id'],
            'date_time': event['date_time'],
            'user_state':event['user_state']
        })) 









## Video message


    
    async def handle_start_video_call(self,text_data_json):


        
        await self.channel_layer.group_send(
        self.room_group_name,
        {
            'type': 'video_call_invite',

            
            'room_name': self.room_name
        }
    )
        
    async def video_call_invite(self, event):

    
     room_name = event['room_name']

     await self.send(text_data=json.dumps({
        'action': 'start_video_call',
        'room_name': room_name
    }))        
   




    @sync_to_async
    def generate_twilio_token(self, user_id, room_name):
   
         user = User.objects.get(id=user_id)
         return generate_twilio_token(user.username, room_name)


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
                
                return  {'exist':False,'value':''}
    
    @database_sync_to_async
    def delete_message(self, message_id):
        message = Message.objects.get(id=message_id)
        message.delete()
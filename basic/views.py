from django.views import View
from django.http import JsonResponse,HttpResponse
from .forms import *
from .services import *
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
import os
from urllib.parse import quote


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
   
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        form = UserRegisterForm(data)
        if form.is_valid():
            try:
                info_obj , user  =   create_user(form.cleaned_data)
                token = generate_token(user)
                token_obj = {
                    'refresh':str(token),
                    'access':str(token.access_token)
                }


                return JsonResponse({
                    'token_obj':token_obj,
                    'user_info':info_obj
                                     })
            except Exception as e:
                return JsonResponse({'errors': 'An error occurred'}, status=500)
            
        return JsonResponse({'errors': form.errors}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        form = UserLoginForm(data)

        if form.is_valid():
            username = data['username']
            password = data['password']
            info_obj,user  = verify_user(username=username,password=password)
            if user:
                token = generate_token(user)
                token_obj = {
                    'refresh':str(token),
                    'access':str(token.access_token)
                }

                return JsonResponse({
                    'token_obj':token_obj,
                    'user_info':info_obj
                                     })
            else:
                return JsonResponse({'error': 'Wrong credentials'}, status=404)
        else:
            return JsonResponse({'errors': form.errors}, status=400)    


class GetUsersView(View):

      def get(self, request, *args, **kwargs):
          response = get_all_users()
          return JsonResponse({'users':response},status=200)      




@method_decorator(csrf_exempt, name='dispatch')
class TokenValidationView(View):
    def get(self, request, *args, **kwargs):
        auth = JWTAuthentication()
        try:
            
            user_auth_tuple = auth.authenticate(request)
            if user_auth_tuple is not None:
                user, token = user_auth_tuple
                return JsonResponse({'message': 'Token is valid', 'user': user.username}, status=200)
            else:
                return JsonResponse({'error': 'Token is invalid or expired'}, status=401)
        except Exception as e:
            return JsonResponse({'error': 'Authentication failed', 'details': str(e)}, status=401)


@method_decorator(csrf_exempt, name='dispatch')
class InvitationView(View):


    def post(self, request, *args, **kwargs):
            data = json.loads(request.body.decode('utf-8'))
            form = InvitationForm(data)
            
            if form.is_valid():
                try:
                     create_invitation(form.cleaned_data)
                      
                     return JsonResponse({'message':"success"},status=200)    
                except Exception as e :
                     return JsonResponse({'errors': 'An error occurred'}, status=500)                
                    
            else:
                return JsonResponse({'errors': form.errors}, status=400)
    


    def put(self, request, *args, **kwargs):
          data = json.loads(request.body.decode('utf-8'))
          print(data)
          try:
             
             accept_invitation(data)
             return JsonResponse({'message':'success'},status=200)
          except Exception as e :
                     print(e)
                     return JsonResponse({'errors': 'An error occurred'}, status=500)   
        
 

    def delete(self, request, *args, **kwargs):   
            data = json.loads(request.body.decode('utf-8'))
       
        
            try:
             refuse_invitation(data)
             return JsonResponse({'message':'success'},status=200)
            except Exception as e :
                     return JsonResponse({'errors': 'An error occurred'}, status=500)                
                    



    def get(self, request, *args, **kwargs):
       try: 
         data = json.loads(request.body.decode('utf-8'))
         uid = data.get('uid')
        
         if not uid:
            raise ValueError("User ID (uid) is required.")
         invitations = get_user_invitaions(uid)
         if isinstance(invitations, str):
            return JsonResponse({'error': invitations}, status=400)
         if not invitations.exists():
            
            return JsonResponse({'invitations': []}, status=200)
         
         invitations_data = [{
            'sid': invitation.sender.id,
            'send_time': invitation.send_time,
            
         } for invitation in invitations]
         print("invitations---------------------------")
         print(invitations_data)
         return JsonResponse({'invitations': invitations_data}, status=200)
       except Exception as e: 
           return JsonResponse({'error': f"An unexpected error occurred: {str(e)}"}, status=500) 




class FriendView(View):

    def get(self, request, *args, **kwargs):
       try: 
         data = json.loads(request.body.decode('utf-8'))
         uid = data.get('uid')
         friend = data.get('friend')
         if not uid:
            raise ValueError("User ID (uid) is required.")
         if friend == True:
             list = get_user_friends(uid)
         else:
             list = get_peoples(uid)

         if isinstance(list, str):
            return JsonResponse({'error': list}, status=400)
         
         if list==[]:
            return JsonResponse({'list': []}, status=200)
         
        
         return JsonResponse({'list': list}, status=200)
       except Exception as e: 
           return JsonResponse({'error': f"An unexpected error occurred: {str(e)}"}, status=500) 



class MessageView(View):
    
    
    def get(self, request, *args, **kwargs):
        
        try:

          data = json.loads(request.body.decode('utf-8'))
          audio = data.get('audio')
          if not(audio is None):
              
              audio_file = data.get('audio_file')
              if audio_file.startswith('/'):
                audio_file = audio_file[1:]
              if audio_file.startswith('media/'):
                audio_file = audio_file[6:]
              file_path =os.path.join(settings.MEDIA_ROOT, audio_file)
              
              if not os.path.exists(file_path):
                return JsonResponse({'error': 'File not found'}, status=404)
              with open(file_path, 'rb') as f:
                    audio_data = f.read()

              response = HttpResponse(audio_data, content_type='audio/wav')
              response['Content-Disposition'] =  f'attachment; filename="{quote(os.path.basename(audio_file))}"'
              return response
          else:
            sender_id = data.get('sender_id')
            receiver_id = data.get('receiver_id')
            min_date_time = data.get('min_date_time')

            if min_date_time is None:
             messages = get_chat_messages(sender_id,receiver_id,None)
            
            else:
                
                messages = get_chat_messages(sender_id,receiver_id,min_date_time)
               

            if isinstance(messages, str):
             return JsonResponse({'error': messages}, status=400)
            if not messages.exists():
              return JsonResponse({'messages': []}, status=200)
            
            messages_data = [{
                'date_time':message.date_time,
                'message_id':message.id,
                'sender': message.sender_id,
                'receiver':message.receiver_id,
                'type':message.message_type,
                'audio_file':message.audio_file.url if message.audio_file else '',
                'image_file':message.image_file.url if message.image_file else '',
                'text_content':message.text_content
            
             } for message in messages]
            
            print(receiver_id)
            receiver = User.objects.get(id=receiver_id)
            user_info = UserInfo.objects.get(user=receiver)
            last_connected = user_info.last_date_connected.isoformat()
            print(last_connected)
            
            return JsonResponse({'messages': messages_data,'user_state':last_connected}, status=200)
        
        
        except Exception as e: 
           print(e)
           return JsonResponse({'error': f"An unexpected error occurred: {str(e)}"}, status=500) 

   









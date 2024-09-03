from django.views import View
from django.http import JsonResponse
from .forms import *
from .services import *
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.authentication import JWTAuthentication


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
   
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        form = UserRegisterForm(data)
        if form.is_valid():
            try:
                user  =   create_user(form.cleaned_data)
                token = generate_token(user)
                token_obj = {
                    'refresh':str(token),
                    'access':str(token.access_token)
                }

                return JsonResponse({'message':token_obj})
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
            user = verify_user(username=username,password=password)
            if user:
                token = generate_token(user)
                token_obj = {
                    'username':username,
                    'token':str(token.access_token)
                }

                return JsonResponse(token_obj)
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
class FriendshipView(View):


    def post(self, request, *args, **kwargs):
            data = json.loads(request.body.decode('utf-8'))
            form = FriendshipForm(data)
            
            if form.is_valid():
                try:
                     create_friend_ship(form.cleaned_data)
                    
                     return JsonResponse({'message':"success"},status=200)    
                except Exception as e :
                     return JsonResponse({'errors': 'An error occurred'}, status=500)                
                    
            else:
                return JsonResponse({'errors': form.errors}, status=400)
    


    def put(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        form = FriendshipForm(data)
        if form.is_valid():
            try:
             accept_friend_ship(form.cleaned_data)
             return JsonResponse(status=200)
            except Exception as e :
                     return JsonResponse({'errors': 'An error occurred'}, status=500)                
                    
        else:
                return JsonResponse({'errors': form.errors}, status=400)
        


    def delete(self, request, *args, **kwargs):   
        data = json.loads(request.body.decode('utf-8'))
        form = FriendshipForm(data)
        if form.is_valid(): 
            try:
             refuse_friend_ship(form.cleaned_data)
             return JsonResponse(status=200)
            except Exception as e :
                     return JsonResponse({'errors': 'An error occurred'}, status=500)                
                    
        else:
                return JsonResponse({'errors': form.errors}, status=400)


    def get(self, request, *args, **kwargs):
       try: 
         data = json.loads(request.body.decode('utf-8'))
         uid = data.get('uid')
         if not uid:
            raise ValueError("User ID (uid) is required.")
         invitations = get_user_invitaions(data)
         if isinstance(invitations, str):
            return JsonResponse({'error': invitations}, status=400)
         if not invitations.exists():
            return JsonResponse({'invitations': []}, status=200)
         invitations_data = [{
            'sender': invitation.sender.id,
            'send_time': invitation.send_time,
            
         } for invitation in invitations]
        
         return JsonResponse({'invitations': invitations_data}, status=200)
       except Exception as e: 
           return JsonResponse({'error': f"An unexpected error occurred: {str(e)}"}, status=500) 






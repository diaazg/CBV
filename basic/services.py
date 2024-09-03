from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .models import UserInfo,Friendship
from django.utils import timezone

def create_user(data):
    try:
        username = data['username']
        email = data['email']
        password = data['password']
        user = User.objects.create_user(username=username, password=password, email=email)
        return user
    except ValidationError as e:
        
        raise e
    except Exception as e:
        
        raise e

     

def get_all_users():
    users = User.objects.all()
    list_users = list(users.values('id', 'username', 'email'))
    return list_users


def generate_token(user):
    
    refresh = RefreshToken.for_user(user)
    return refresh


def verify_user(username, password):
    try:
        
        user = User.objects.get(username=username)
        if check_password(password, user.password):
            return user
        else:
            return None
    except User.DoesNotExist:
        return None
    

def update_last_connected_date(user):
            user_info, created = UserInfo.objects.get_or_create(user=user)
            user_info.last_date_connected = timezone.now()
            user_info.save()






def create_friend_ship(data):
     try:
          sender = data['sender']
          receiver = data['receiver'] 
          
         
          Friendship.objects.create(sender=sender,receiver=receiver)   



     except  Exception as e:
          
          raise ValidationError(e)    
     



def accept_friend_ship(data):
        try:
               sid = data['sender']
               rid = data['receiver']
               receiver = User.objects.get(id=rid)
               sender = User.objects.get(id=sid)
               friendship = Friendship.objects.get(sender=sender,receiver=receiver)
               friendship.accepted = True
               
               friendship.last_connection = timezone.now()
               friendship.save()
        except Exception as e :
             raise ValidationError(e)   



def refuse_friend_ship(data):
        try:
               sid = data['sender']
               rid = data['receiver']
               receiver = User.objects.get(id=rid)
               sender = User.objects.get(id=sid)
               friendship = Friendship.objects.get(sender=sender,receiver=receiver,accepted=False)
               friendship.delete()
        except Exception as e :
             raise ValidationError(e)   
     

def get_user_invitaions(data):
      try:
        uid = data['uid']
        receiver = User.objects.get(id=uid)
        invitations = Friendship.objects.filter(receiver=receiver).order_by('send_time')
        return invitations
      except User.DoesNotExist:
        return "User not found."
      except ValueError as ve:
        return str(ve)
      except Exception as e:
           return e

               
     
     
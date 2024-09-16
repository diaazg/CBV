from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .models import *
from django.utils import timezone
from django.db.models import Q
from datetime import datetime

def create_user(data):
    try:
        username = data['username']
        email = data['email']
        password = data['password']
        phone_number = data['phone_number']
        profile_title = data['profile_title']
        user = User.objects.create_user(username=username, password=password, email=email)
        user_info = UserInfo.objects.create(user=user,phone_number=phone_number)
        user_profile = Profile.objects.create(user=user,title=profile_title)
        uid = user.id
        info_obj = {
             'uid':uid,
             'username':username,
             'email':email,
             'password':password,
             'phone_number':phone_number,
              'profile_title':profile_title

        }
        return info_obj , user
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
            user_info = UserInfo.objects.get(user=user)
            user_profile = Profile.objects.get(user=user)
           
            uid = user.id
            info_obj = {
             'uid':uid,
             'username':username,
             'email':user.email,
             'password':password,
             'phone_number':str(user_info.phone_number),
              'profile_title':user_profile.title

               }
            return info_obj,user 
        else:
            return None,None
    except User.DoesNotExist:
        return None,None
    

def update_last_connected_date(user):
            user_info, created = UserInfo.objects.get_or_create(user=user)
            user_info.last_date_connected = timezone.now()
            user_info.save()






def create_invitation(data):
     try:
          sender = data['sender']
          receiver = data['receiver'] 
          
         
          Invitation.objects.create(sender=sender,receiver=receiver)   



     except  Exception as e:
          
          raise ValidationError(e)    
     



def accept_invitation(data):
        try:
               sid = data['sender']
               rid = data['receiver']
               print(sid)
               print(rid)
               room = f'{sid}_{rid}'
               receiver = User.objects.get(id=rid)
               sender = User.objects.get(id=sid)
               inv = Invitation.objects.get(sender=sender,receiver=receiver)
               print(inv)
               Invitation.objects.get(sender=sender,receiver=receiver).delete()
               Friend.objects.create(sender=sender,receiver=receiver)
               Room.objects.create(name=room)

        except Exception as e :
             raise ValidationError(e)   



def refuse_invitation(data):
        try:
               sid = data['sender']
               rid = data['receiver']
               receiver = User.objects.get(id=rid)
               sender = User.objects.get(id=sid)
               invitation = Invitation.objects.get(sender=sender,receiver=receiver)
               invitation.delete()
        except Exception as e :
             raise ValidationError(e)   
     

def get_user_invitaions(uid):
      try:
        
        receiver = User.objects.get(id=uid)
        invitations = Invitation.objects.filter(receiver=receiver).order_by('send_time')
        return invitations
      except User.DoesNotExist:
        return "User not found."
      except ValueError as ve:
        return str(ve)
      except Exception as e:
           return e

               


def get_user_friends(uid):
      try:
        
        user = User.objects.get(id=uid)
        
        friends = Friend.objects.filter(Q(receiver=user)|Q(sender=user)).order_by('accept_time')
        
        friends_list = []
        for friend in friends:
             if(friend.sender == user):
                 my_friend = friend.receiver
             else:  
                 my_friend = friend.sender
             obj = {
                 'friend_id': my_friend.id,
                 'friend_name':my_friend.username,
                 'accept_time': friend.accept_time,

             }
             friends_list.append(obj)
           
        
        return friends_list
      except User.DoesNotExist:
        return "User not found."
      except ValueError as ve:

        return str(ve)
      except Exception as e:
           return e
     


def get_peoples(uid):
      try:
        friends = Friend.objects.filter(Q(sender_id=uid) | Q(receiver_id=uid))
        invitations = Invitation.objects.filter(Q(sender_id=uid) | Q(receiver_id=uid))
        friend_ids = friends.values_list('sender_id', 'receiver_id')
        invitation_ids = invitations.values_list('sender_id', 'receiver_id')
        excluded_ids = set(
                            list(friend_ids.values_list('sender_id',flat=True)) +
                            list(friend_ids.values_list('receiver_id',flat=True)) + 
                            list(invitation_ids.values_list("sender_id",flat=True)) +
                            list(invitation_ids.values_list("receiver_id",flat=True))
                            )
        print(excluded_ids)

        peoples = User.objects.exclude(id__in=excluded_ids)
        
        
        peoples_list = []
        for person in peoples:
             
             obj = {
                 'uid': person.id,
                 'username':person.username,
             }
             peoples_list.append(obj)
           
        
        return peoples_list
      except User.DoesNotExist:
        return "User not found."
      except ValueError as ve:

        return str(ve)
      except Exception as e:
           return e     



def get_chat_messages(sender_id,receiver_id,get_new):

      try:   
  
           sender = User.objects.get(id=sender_id)
           receiver = User.objects.get(id=receiver_id)
           
           if get_new is None :
              messages = Message.objects.filter(
                  (
                       Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
                          )
                   ).order_by('-date_time')[:20]

           else:
              parsed_date = datetime.strptime(get_new, '%Y-%m-%dT%H:%M:%SZ')
              messages = Message.objects.filter(
                  (
                       ( Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender) )
                       & 
                       Q(date_time__lt=parsed_date)
                       )
                   ).order_by('-date_time')[:20]

           return messages
      

      except User.DoesNotExist:
        return "User not found."
      except ValueError as ve:
        return str(ve)
      except Exception as e:
           return e


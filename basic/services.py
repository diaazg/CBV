from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

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
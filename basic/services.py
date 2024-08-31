from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
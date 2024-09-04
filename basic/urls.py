from django.urls import path, include,re_path
from .views import *
from .consumers import  DirectChatConsumer





urlpatterns = [
    path('register', RegisterView.as_view(),name='register'),
    path('login', LoginView.as_view(),name='login'),
    path('getall', GetUsersView.as_view(),name='get_all'),
    path('checkToken',TokenValidationView.as_view()),
    path('invitation',InvitationView.as_view()),
    path('friend',FriendView.as_view()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', DirectChatConsumer.as_asgi()),  

    
    
]

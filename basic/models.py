from django.db import models
from django.contrib.auth.models import User


class UserInfo(models.Model):
    
    user = models.OneToOneField(User,on_delete=models.CASCADE)

    country = models.CharField(max_length=100)
    phoneNumber = models.CharField(max_length=10)


    def __str__(self) -> str:
        return self.user.username

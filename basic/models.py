from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone


class UserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField()
    last_date_connected = models.DateTimeField()
    last_date_inv = models.DateTimeField(null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.pk:  # Object is being created
            self.last_date_connected = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.user.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=80)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username}"


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    is_seen = models.BooleanField(default=False)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:50]}"


class Invitation(models.Model):
    sender = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    send_time = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self) -> str:
        return f"Friendship request from {self.sender.username} to {self.receiver.username}"


class Friend(models.Model):
    sender = models.ForeignKey(User, related_name='sender_friend', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver_friend', on_delete=models.CASCADE)
    accept_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self) -> str:
        return f"Friendship request from {self.sender.username} to {self.receiver.username}"
    


class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='stories/')
    post_date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username}'s Story"

class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
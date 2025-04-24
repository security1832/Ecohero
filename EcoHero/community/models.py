from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class Post(models.Model):
    image = models.ImageField(upload_to='posts/', null=True)
    title = models.CharField(max_length=20, null=False)
    content = models.TextField(max_length=500, blank=False, null=False)
    posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def total_likes(self):
        return self.likes.count()

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name = 'comments')
    content = models.TextField()
    commented_at = models.DateTimeField(auto_now_add=True)

class Likes(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['post', 'user']

class EcoStory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    caption = models.TextField(blank=True)
    image = models.ImageField(upload_to='eco_stories/', blank=True, null=True)
    vedio = models.FileField(upload_to='eco_stories/vedios/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_highlight = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

class VedioRoom(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    def jitsi_url(self):
        return f"https://meet.jit.si/{self.name.replace(' ', '')}"
    
class ChatRoom(models.Model):
    ROOM_TYPES = (
        ('dm', 'Direct Message')
        ('group', 'Group Chat')
        ('public', 'Public Channel')
    )

    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='dm')
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    admins = models.ManyToManyField(User, related_name='admin_chat_rooms', blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_admin(self, user):
        return self.admins.filter(id=user.id).exists()

    def __str__(self):
        return f"Room {self.id} ({self.get_room_type_display()})"
    
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender =models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('message', 'New Message'),
        ('mention', 'Mention'),
        ('group_invite', 'Group Invite'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} to {self.user.username}" 
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    if created:
        room = instance.room
        for user in room.participants.all():
            if user != instance.sender:
                Notification.objects.create(
                    user=user,
                    notification_type='message',
                    message=instance,
                    chat_room=room,
                    content=f"New message from {instance.sender.username}"
                )

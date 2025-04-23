from celery import shared_task
from django.utils import timezone
from .models import EcoStory

@shared_task
def delete_expired_stories():
    expired = EcoStory.objects.filter(expires_at__lt=timezone.now())
    count = expired.count()
    expired.delete()
    return f"Deleted {count} expired stories."

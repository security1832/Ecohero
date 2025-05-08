from rest_framework.permissions import BasePermission # type: ignore
from .models import UserSubscription
from django.utils import timezone

class HasActiveSubscription(BasePermission):
    def has_permission(self, request, view):
        try:
            subscription = UserSubscription.objects.get(user=request.user)
            return subscription.active and subscription.end_date > timezone.now()
        except UserSubscription.DoesNotExist:
            return False

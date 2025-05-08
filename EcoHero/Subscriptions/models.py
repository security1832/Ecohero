from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.IntegerField()
    features = models.TextField()
    external_id = models.CharField(max_length=100, bank=True)

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)
    payment_provider = models.CharField(max_length=30, choices=[('stripe', 'Stripe'), ('paypal', 'Paypal'), ('coinbase', 'Coinbase')])

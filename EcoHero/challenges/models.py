from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Challenge(models.Model):
    name = models.CharField(max_length=20, blank=False, null=False)
    description  = models.TextField()
    carbon_saved = models.CharField(max_length=100, blank=False, null=False)
    xp_reward = models.PositiveIntegerField(default=0)

class UserChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

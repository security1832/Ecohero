from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Badge(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/', blank=True, null=True)
    level = models.CharField(max_length=20, default='Bronze')

    def __str__(self):
        return self.name
    
class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.icon}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_img = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(max_length=300, null=True)
    total_carbon_saved = models.IntegerField(null=True)
    total_xp_earned = models.PositiveIntegerField(default=0)
    total_challenges = models.IntegerField(default=0, null=False)
    badge = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username
    


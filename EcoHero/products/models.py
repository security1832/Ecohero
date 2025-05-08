from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.

class Product(models.Model):
    image = models.ImageField(upload_to='products_images/', null=True)
    name = models.CharField(max_length=20, null=False)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    description = models.TextField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    carbon_saved = models.CharField(max_length=50, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    eco_rating = models.IntegerField(choices=[(i, i) for i in range(1,6)], null=False)

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
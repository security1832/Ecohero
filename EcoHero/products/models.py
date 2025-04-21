from django.db import models

# Create your models here.

class Product(models.Model):
    image = models.ImageField(upload_to='products_images/', null=True)
    name = models.CharField(max_length=20, null=False)
    description = models.TextField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    carbon_saved = models.CharField(max_length=50, null=False)
    eco_rating = models.IntegerField(choices=[(i, i) for i in range(1,6)], null=False)




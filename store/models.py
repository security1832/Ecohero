from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse # Import reverse

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.id, self.slug])

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, related_name='shipping_addresses', on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default="Kenya") # Default to Kenya
    phone_number = models.CharField(max_length=20)
    default = models.BooleanField(default=False) # To mark a default shipping address for a user

    def __str__(self):
        return f"{self.full_name}, {self.address_line_1}, {self.city}"

    class Meta:
        verbose_name_plural = "Shipping Addresses"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True) # Allow anonymous orders initially if needed, or link to user
    shipping_address = models.ForeignKey(ShippingAddress, related_name='orders', on_delete=models.PROTECT, null=True, blank=True) # Protect address if orders depend on it
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, default='Payment on Delivery')
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending_payment')
    # Billing address can be added if different from shipping
    # billing_address = models.ForeignKey(ShippingAddress, related_name='billing_for_orders', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Order {self.id} by {self.user.username if self.user else 'Guest'}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE) # Or models.SET_NULL if product can be deleted but order item should remain
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at the time of order
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in order {self.order.id}"

    def get_cost(self):
        return self.price * self.quantity

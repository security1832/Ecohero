from ..models import *
from rest_framework import serializers # type: ignore

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'image', 'description', 'price', 'carbon_saved', 'eco_rating' ]

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=CartItem
        fields=['id', 'user', 'product', 'quantity', 'added_at']
        read_only_fields = ['user', 'added_at']
from ..models import *
from rest_framework import serializers # type: ignore

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'image', 'description', 'price', 'carbon_saved', 'eco_rating' ]
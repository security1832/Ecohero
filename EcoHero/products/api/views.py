from ..models import *
from rest_framework.response import Response # type: ignore
from rest_framework import status, generic # type: ignore
from rest_framework.decorators import api_view # type: ignore
from .serializers import ProductSerializer

@api_view(['GET'])
def view_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

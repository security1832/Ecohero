from warnings import filters
from ..models import *
from rest_framework.response import Response # type: ignore
from rest_framework import status, permissions # type: ignore
from rest_framework.decorators import api_view # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.exceptions import PermissionDenied # type: ignore
from rest_framework.generics import RetrieveUpdateDestroyAPIView # type: ignore
from .serializers import *
from rest_framework.generics import ListCreateAPIView, DestroyAPIView # type: ignore

class ProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.all().order_by('-name')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class ProductRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    products = Product.object.all()
    serializer = ProductSerializer()

    def perform_update(self, serializer):
        if self.request.user != self.get_object().seller:
            raise PermissionDenied("Not allowed to efit this Product!!")
        serializer.save()

    def perform_delete(self, instance):
        if self.request.user != instance.seller:
            raise PermissionDenied("Not allowed to delete this Product!!")
        instance.delete()

class CartListCreateView(ListCreateAPIView):
    serializer = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self):
        return CartItem.objects.filter(user=self.request.user)
    
    def post(self, serializer):
        serializer.save(user=self.request.user)

class CartItemDeleteView(DestroyAPIView):
    queryset = CartItem.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer

    def get(self):
        return CartItem.objects.filter(user=self.request.user)
from django.urls import path
from .views import *

urlpatterns = [
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),

    path('cart/', CartListCreateView.as_view(), name='cart'),
    path('cart/<int:pk>/', CartItemDeleteView.as_view(), name='cart-delete'),
]
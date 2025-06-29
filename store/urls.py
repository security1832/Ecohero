from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # Product catalog URLs
    path('', views.product_list, name='product_list'), # Root URL for the store app, shows all products
    path('search/', views.product_list, name='product_search'), # For search results, reuses product_list view
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),

    # Cart URLs
    path('cart/', views.cart_detail, name='cart_detail'), # Replaces cart_view
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    # Checkout URLs
    path('checkout/', views.checkout, name='checkout'), # Was checkout_placeholder
    path('order/<int:order_id>/', views.order_detail_view, name='order_detail'),
]

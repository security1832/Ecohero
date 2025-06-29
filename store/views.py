from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse # Import reverse
from django.views import generic # For LoginView if needed, but usually handled in urls.py
from .models import Order, OrderItem, Product, Category, ShippingAddress # Import OrderItem, ShippingAddress
from .cart import Cart # Import the Cart class
from .forms import CartAddProductForm, ShippingAddressForm # Import ShippingAddressForm
from django.db.models import Q # For search
from django.db import transaction # For atomic transactions


# Registration View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login') # Redirect to Django's built-in login URL name
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Profile View
@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/profile.html', {'orders': orders})


# Product Catalog Views
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    query = request.GET.get('q')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request,
                  'store/product/list.html',
                  {'category': category,
                   'categories': categories,
                   'products': products,
                   'query': query})

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm(initial={'quantity': 1, 'update': False}) # Add initial quantity
    return render(request,
                  'store/product/detail.html',
                  {'product': product,
                   'cart_product_form': cart_product_form})

# Cart Views
@require_POST # Ensures this view only accepts POST requests
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        # Check against available stock
        if product.stock >= cd['quantity']:
            cart.add(product=product,
                     quantity=cd['quantity'],
                     update_quantity=cd['update'])
            messages.success(request, f"'{product.name}' added to your cart.")
        else:
            messages.error(request, f"Not enough stock for '{product.name}'. Only {product.stock} available.")

    return redirect(request.POST.get('next', reverse('store:cart_detail')))


@require_POST # Ensures this view only accepts POST requests (or use a different method for links)
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"'{product.name}' removed from your cart.")
    return redirect('store:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    for item in cart: # Prepare forms for updating quantities in the cart
        item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'update': True})
    return render(request, 'store/cart/detail.html', {'cart': cart})

# This replaces the old placeholder cart_view
# def cart_view(request):
#     return render(request, 'store/base.html', {'content': 'Cart View Placeholder - To be implemented'}) # Temporary


# Checkout View
@login_required
def checkout(request):
    cart = Cart(request)
    if not cart: # if cart is empty
        messages.info(request, "Your cart is empty. Add some products before checking out.")
        return redirect('store:product_list')

    # Try to get user's last used or default shipping address
    last_shipping_address = ShippingAddress.objects.filter(user=request.user, default=True).first()
    if not last_shipping_address:
        last_shipping_address = ShippingAddress.objects.filter(user=request.user).last()

    if request.method == 'POST':
        shipping_form = ShippingAddressForm(request.POST, instance=last_shipping_address)
        if shipping_form.is_valid():
            try:
                with transaction.atomic():
                    shipping_address = shipping_form.save(commit=False)
                    shipping_address.user = request.user
                    # Logic to set as default if a checkbox "Set as default" is added to the form
                    # if shipping_form.cleaned_data.get('set_default'):
                    #    ShippingAddress.objects.filter(user=request.user).update(default=False)
                    #    shipping_address.default = True
                    shipping_address.save()

                    order = Order.objects.create(
                        user=request.user,
                        shipping_address=shipping_address,
                        total_paid=cart.get_total_price(),
                        payment_method='Payment on Delivery',
                        status='processing' # Or 'pending_confirmation' if you want an extra step
                    )
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['quantity']
                        )
                        # Decrease product stock
                        product = item['product']
                        product.stock -= item['quantity']
                        product.save()

                    cart.clear()
                    messages.success(request, 'Thank you! Your order has been placed successfully. We will contact you shortly for delivery.')
                    # TODO: Send order confirmation email (Step 11)
                    return redirect(reverse('store:order_detail', args=[order.id])) # Redirect to an order detail page

            except Exception as e: # Catch any error during transaction
                messages.error(request, f"An error occurred while processing your order: {e}")
                # Log the error e for debugging
        else:
            messages.error(request, "There was an error with your shipping details. Please check the form.")
    else:
        # Pre-populate form if last_shipping_address exists, else an empty form
        shipping_form = ShippingAddressForm(instance=last_shipping_address)

    return render(request, 'store/checkout/checkout.html', {
        'cart': cart,
        'shipping_form': shipping_form
    })

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user) # Ensure user can only see their own orders
    return render(request, 'store/checkout/order_detail.html', {'order': order})

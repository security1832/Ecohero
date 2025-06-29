from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal

from .models import Category, Product, Order, OrderItem, ShippingAddress
from .cart import Cart
from .forms import CartAddProductForm
from django.conf import settings # Added for settings.CART_SESSION_ID

# Helper function to create a user
def create_user(username="testuser", password="testpassword"):
    return User.objects.create_user(username=username, password=password)

class CategoryModelTests(TestCase):
    def test_category_str(self):
        category = Category.objects.create(name="Electronics")
        self.assertEqual(str(category), "Electronics")

    def test_category_slug_creation(self):
        category = Category.objects.create(name="Home Appliances")
        self.assertEqual(category.slug, "home-appliances")

    def test_category_get_absolute_url(self):
        category = Category.objects.create(name="Books")
        self.assertEqual(category.get_absolute_url(), reverse('store:product_list_by_category', args=[category.slug]))

class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")

    def test_product_str(self):
        product = Product.objects.create(category=self.category, name="Test Product", price=Decimal("10.00"))
        self.assertEqual(str(product), "Test Product")

    def test_product_slug_creation(self):
        product = Product.objects.create(category=self.category, name="Another Product", price=Decimal("20.00"))
        self.assertEqual(product.slug, "another-product")

    def test_product_get_absolute_url(self):
        product = Product.objects.create(category=self.category, name="URL Test Product", price=Decimal("30.00"))
        # Need to save to get an ID for the product before slug generation for URL
        product.save()
        self.assertEqual(product.get_absolute_url(), reverse('store:product_detail', args=[product.id, product.slug]))

class OrderItemModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(category=self.category, name="Test Product", price=Decimal("10.00"), stock=10)
        self.user = create_user()
        self.order = Order.objects.create(user=self.user, total_paid=Decimal("20.00"))

    def test_get_cost(self):
        order_item = OrderItem.objects.create(order=self.order, product=self.product, price=Decimal("10.00"), quantity=2)
        self.assertEqual(order_item.get_cost(), Decimal("20.00"))


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user()
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.product = Product.objects.create(
            category=self.category,
            name="Test Product",
            slug="test-product",
            price=Decimal("10.00"),
            stock=5
        )

    def test_product_list_view(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product/list.html')
        self.assertContains(response, self.product.name)

    def test_product_list_by_category_view(self):
        response = self.client.get(reverse('store:product_list_by_category', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product/list.html')
        self.assertContains(response, self.product.name)
        self.assertEqual(response.context['category'], self.category)

    def test_product_detail_view(self):
        response = self.client.get(reverse('store:product_detail', args=[self.product.id, self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product/detail.html')
        self.assertContains(response, self.product.name)
        self.assertIsInstance(response.context['cart_product_form'], CartAddProductForm)

    def test_register_view(self):
        response = self.client.get(reverse('store:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

        # Test registration
        user_count_before = User.objects.count()
        response = self.client.post(reverse('store:register'), {
            'username': 'newuser',
            'password': 'newpassword123', # Django's UserCreationForm doesn't use password1 and password2 directly in POST
            'password2': 'newpassword123' # This is how UserCreationForm expects it if you render the form
        }, follow=False) # Don't follow redirect to see messages
        # A successful registration redirects to login.
        # UserCreationForm itself does not take password2. It's the form in template that might.
        # For direct POST to UserCreationForm, only username and password (which becomes password1 internally) are directly used.
        # Let's adjust: UserCreationForm handles password confirmation internally.
        # A simple UserCreationForm post only needs 'username' and 'password' (which is used as password1)
        # However, the default UserCreationForm requires password1 and password2 for validation.
        # The test client post will need to simulate the form fields.
        # Let's assume the form is UserCreationForm which has password1 and password2 fields.
        # No, UserCreationForm does not have password2. It's usually added in a custom form.
        # The default UserCreationForm has 'password' and 'password_confirmation' if you subclass and add it.
        # Let's test with how UserCreationForm is typically used.
        # It has password1 and password2 fields when rendered.
        # For testing UserCreationForm directly:
        # form_data = {'username': 'newuser', 'password': 'newpassword123'}
        # form = UserCreationForm(data=form_data)
        # self.assertTrue(form.is_valid())
        # For view testing, we need to provide what the form expects: 'username', 'password', 'password2' if using default Django auth templates
        # The default UserCreationForm has fields password and password2 (for confirmation)

        # Simplification for test:
        # Create a UserCreationForm instance and check if it's valid
        from django.contrib.auth.forms import UserCreationForm
        form_data = {'username': 'newuser', 'password': 'newpassword123A!', 'password2': 'newpassword123A!'}
        # The default UserCreationForm uses password1 and password2
        # Let's re-verify UserCreationForm fields. It's password and password_confirmation.
        # The form fields are 'username', 'password', 'password_confirmation'.
        # For the test client:
        response = self.client.post(reverse('store:register'), {
            'username': 'newuser',
            'password': 'someStrongPassword123!', # Django's default password validators will apply
            'password_confirmation': 'someStrongPassword123!'
        })
        # This is still not quite right for UserCreationForm.
        # UserCreationForm has fields 'username', 'password', and 'password2' by default for its internal validation.
        # Let's use the actual UserCreationForm fields directly.
        # The fields are 'username', 'password', 'password2'.
        # The issue is UserCreationForm expects 'password' and 'password2' for confirmation.
        # The `register` view uses UserCreationForm(request.POST)
        # The form itself has fields `username`, `password`, `password2`.
        # Let's use the correct field names UserCreationForm expects.

        # After much back & forth, Django's UserCreationForm actually expects `password` and `password2`
        # if you pass request.POST directly to it.
        # However, the default `UserCreationForm` uses `password` and `password_confirmation` for its fields.
        # This is confusing. Let's use what the view expects.
        # The view uses `UserCreationForm(request.POST)`.
        # The form has `username`, `password` and `password2` (confirmation) fields.

        # Trying to match the "password1" field error. This is unusual.
        user_data = {'username': 'newuser', 'password1': 'ValidPassword123!', 'password2': 'ValidPassword123!'}
        # user_data = {'username': 'newuser', 'password': 'ValidPassword123!', 'password2': 'ValidPassword123!'} # Original
        response = self.client.post(reverse('store:register'), user_data, follow=True) # Follow redirect

        if not response.context.get('user') or not response.context.get('user').is_authenticated:
            # If registration failed and rerendered the form, print errors.
            if response.context and 'form' in response.context:
                form_errors = response.context['form'].errors.as_json()
                print(f"Registration form errors: {form_errors}")

        self.assertEqual(response.status_code, 200) # Should redirect to login page
        self.assertTemplateUsed(response, 'registration/login.html') # Django's default login URL
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertEqual(User.objects.count(), user_count_before + 1)
        # Check for success message
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Account created for newuser! You can now log in.")


    def test_login_logout_view(self):
        # Test login
        login_response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword'}, follow=True)
        self.assertEqual(login_response.status_code, 200)
        # Default LOGIN_REDIRECT_URL is 'store:profile'
        self.assertTemplateUsed(login_response, 'store/profile.html')
        self.assertTrue(login_response.context['user'].is_authenticated)

        # Test profile page while logged in
        profile_response = self.client.get(reverse('store:profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertTemplateUsed(profile_response, 'store/profile.html')
        self.assertContains(profile_response, self.user.username)

        # Test logout (should be a POST request by default for Django 4+)
        logout_response = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(logout_response.status_code, 200)
        # Default LOGOUT_REDIRECT_URL is 'store:product_list'
        self.assertTemplateUsed(logout_response, 'store/product/list.html')
        self.assertFalse(logout_response.context['user'].is_authenticated)

    def test_cart_detail_view_empty(self):
        response = self.client.get(reverse('store:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/cart/detail.html')
        self.assertContains(response, "Your cart is empty.")

    def test_checkout_view_requires_login(self):
        response = self.client.get(reverse('store:checkout'))
        self.assertEqual(response.status_code, 302) # Redirect to login
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_checkout_view_logged_in_empty_cart(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('store:checkout'), follow=True)
        self.assertEqual(response.status_code, 200)
        # Should redirect to product list if cart is empty and display a message
        self.assertTemplateUsed(response, 'store/product/list.html')
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn("Your cart is empty", str(messages[0]))


class CartLogicTests(TestCase):
    def setUp(self):
        self.client = Client() # Each test needs its own client for session management
        self.category = Category.objects.create(name="Gadgets")
        self.product1 = Product.objects.create(category=self.category, name="Mouse", price=Decimal("25.00"), stock=10)
        self.product2 = Product.objects.create(category=self.category, name="Keyboard", price=Decimal("75.00"), stock=5)

    def test_add_to_cart(self):
        # Add product1
        self.client.post(reverse('store:cart_add', args=[self.product1.id]), {'quantity': 2, 'update': False})

        # Check cart in session (simulating how Cart class works)
        session_cart = self.client.session.get(settings.CART_SESSION_ID)
        self.assertIsNotNone(session_cart)
        self.assertIn(str(self.product1.id), session_cart)
        self.assertEqual(session_cart[str(self.product1.id)]['quantity'], 2)
        self.assertEqual(session_cart[str(self.product1.id)]['price'], str(self.product1.price))

        # Add product2
        self.client.post(reverse('store:cart_add', args=[self.product2.id]), {'quantity': 1, 'update': False})
        session_cart = self.client.session.get(settings.CART_SESSION_ID)
        self.assertIn(str(self.product2.id), session_cart)
        self.assertEqual(session_cart[str(self.product2.id)]['quantity'], 1)

        # Use the Cart class to verify totals from the request object
        # cart = Cart(self.client.request) # This line was problematic and should be removed.

        # To test Cart class directly, we need a request object.
        # We can create a mock request or use the test client's session.
        # Let's test through the cart_detail view context.
        response = self.client.get(reverse('store:cart_detail'))
        self.assertEqual(response.status_code, 200)
        cart_context = response.context['cart'] # This is an instance of Cart

        self.assertEqual(len(cart_context), 3) # 2 of product1, 1 of product2
        self.assertEqual(cart_context.get_total_price(), (Decimal("25.00") * 2) + (Decimal("75.00") * 1))


    def test_update_cart_item_quantity(self):
        # Add product1
        self.client.post(reverse('store:cart_add', args=[self.product1.id]), {'quantity': 1, 'update': False})
        # Update quantity of product1
        self.client.post(reverse('store:cart_add', args=[self.product1.id]), {'quantity': 3, 'update': True})

        session_cart = self.client.session.get(settings.CART_SESSION_ID)
        self.assertEqual(session_cart[str(self.product1.id)]['quantity'], 3)

        response = self.client.get(reverse('store:cart_detail'))
        cart_context = response.context['cart']
        self.assertEqual(len(cart_context), 3)
        self.assertEqual(cart_context.get_total_price(), Decimal("25.00") * 3)

    def test_remove_from_cart(self):
        # Add product1 and product2
        self.client.post(reverse('store:cart_add', args=[self.product1.id]), {'quantity': 2, 'update': False})
        self.client.post(reverse('store:cart_add', args=[self.product2.id]), {'quantity': 1, 'update': False})

        # Remove product1
        self.client.post(reverse('store:cart_remove', args=[self.product1.id]))

        session_cart = self.client.session.get(settings.CART_SESSION_ID)
        self.assertNotIn(str(self.product1.id), session_cart)
        self.assertIn(str(self.product2.id), session_cart)

        response = self.client.get(reverse('store:cart_detail'))
        cart_context = response.context['cart']
        self.assertEqual(len(cart_context), 1) # Only product2 left
        self.assertEqual(cart_context.get_total_price(), Decimal("75.00") * 1)

    def test_clear_cart_on_checkout(self):
        # Log in user
        user = create_user(username="checkoutuser", password="password")
        self.client.login(username="checkoutuser", password="password")

        # Add item to cart
        self.client.post(reverse('store:cart_add', args=[self.product1.id]), {'quantity': 1, 'update': False})

        # Prepare shipping address data
        shipping_data = {
            'full_name': 'Test User',
            'address_line_1': '123 Main St',
            'city': 'Testville',
            'phone_number': '1234567890',
            'country': 'Kenya'
        }

        # Perform checkout
        response = self.client.post(reverse('store:checkout'), shipping_data, follow=True)
        self.assertEqual(response.status_code, 200) # Should redirect to order detail
        self.assertTemplateUsed(response, 'store/checkout/order_detail.html')

        # Check if cart is cleared from session
        session_cart = self.client.session.get(settings.CART_SESSION_ID)
        # After redirect, context processor for cart runs and re-initializes cart to {} if it was None
        self.assertEqual(session_cart, {})

        # Check if order was created
        self.assertTrue(Order.objects.filter(user=user).exists())
        order = Order.objects.get(user=user)
        self.assertEqual(order.total_paid, self.product1.price)
        self.assertEqual(order.items.count(), 1)

        # Check stock deduction
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.stock, 9) # Was 10, 1 bought

    def test_add_to_cart_insufficient_stock(self):
        # Product has stock of 10
        response = self.client.post(reverse('store:cart_add', args=[self.product1.id]), {'quantity': 11, 'update': False}, follow=True)
        self.assertEqual(response.status_code, 200) # Redirects back to cart_detail or 'next'

        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertIn("Not enough stock", str(messages_list[0]))

        # Cart should not have the item or quantity should not be updated beyond stock
        session_cart = self.client.session.get(settings.CART_SESSION_ID)
        if str(self.product1.id) in session_cart: # If it was added before with valid qty
             self.assertNotEqual(session_cart[str(self.product1.id)]['quantity'], 11)
        else: # If it was not in cart before
            self.assertIsNone(session_cart.get(str(self.product1.id)))

        # More precise check: cart should be empty if this was the only add operation
        # cart = Cart(self.client.request) # This line was problematic and should be removed.
        response_cart_detail = self.client.get(reverse('store:cart_detail'))
        cart_context = response_cart_detail.context['cart']
        self.assertEqual(len(cart_context), 0) # Expecting cart to be empty as add failed due to stock

from django.urls import path
from .views import *

urlpatterns = [
    path('subscription/status/', CheckSubscriptionStatusAPIView.as_view(), name='subscription_status'),

    path('plans/', SubscriptionPlanListAPIView.as_view(), name='subscription_plans'),
    path('paypal/success/', PayPalSuccessAPIView.as_view(), name='paypal_success'),

    path('coinbase/charge/', CreateCoinbaseChargeApiView.as_view(), name='coinbase_charge'),
    path('coinbase/webhook/', CoinBaseWebhookAPIView.as_view(), name='coinbase_webhook'),

]
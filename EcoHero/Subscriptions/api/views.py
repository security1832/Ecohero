from rest_framework.response import Response #type: ignore
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status # type: ignore
from rest_framework.views import APIView # type: ignore
from .serializers import *
from ..models import *
from django.utils import timezone
from datetime import timedelta
import coinbase_commerce #type: ignore
from coinbase_commerce.client import Client # type: ignore
from ....EcoHero import env
from django.utils.decorators import method_decorator
import hmac, hashlib, json
from ..permissions import HasActiveSubscription

coinbase_commerce.api_key = env.COINBASE_API_KEY

class SubscriptionPlanListAPIView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer = SubscriptionPlanSeriaizer
    permission_classes = [permissions.AllowAny]

class PayPalSuccessAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get("plan_id")
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            subscription, created = UserSubscription.objects.update_or_create(
                user=request.user,
                defaults={
                    "plan": plan,
                    "start_date": timezone.now(),
                    "end_date": timezone.now() + timedelta(days=plan.duration_days),
                    "active": True,
                    "payment_provider": "paypal"
                }
            )
            return Response({"status":"success"}, status=status.HTTP_200_OK)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Invalid plan ID"}, status=status.HTTP_400_BAD_REQUEST)
        
class CreateCoinbaseChargeApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get("plan_id")
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Invalid plan ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        client = Client(api_key=env.COINBASE_API_KEY)
        charge = client.charge.create(
            name=plan.name,
            description = plan.description,
            local_price={"amount": str(plan.price), "currency": "USD"},
            pricing_type = 'fixed_price',
            metadata={
                "user_id": request.user.id,
                "plan_id": plan.id
            }
        )
        return Response({"hosted_url": charge["hosted_url"], "charge_id": charge["id"]}, status=200)
    
class CoinBaseWebhookAPIView(APIView):
    def post(self, request, *args, **Kwargs):

        signature = request.headers.get("X-CC-Webhook-Signature", "")
        payload = request.body
        secret = env.COINBASE_WEBHOOK_SECRET

        computed_signature = hmac.new(
            key=secret.encode(),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(computed_signature, signature):
            event = json.loads(payload)
            if event["event"]["type"] == "charge:confirmed":
                metadata = event["event"]["data"]["metadata"]
                user_id = metadata.get("user_id")
                plan_id = metadata.get("plan_id")

                try:
                    plan = SubscriptionPlan.objects.get(id=plan_id)
                    user = User.objects.get(id=user_id)
                    UserSubscription.objects.update_or_create(
                        user=user,
                        defaults={
                            "plan": plan,
                            "start_date": timezone.now(),
                            "end_date": timezone.now() + timedelta(days=plan.duration_days),
                            "active": True,
                            "payment_provider": "coinbase"
                        }
                    )
                except Exception as e:
                    pass

            return Response(status=200)

        return Response(status=400)
    
class CheckSubscriptionStatusAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            subscription = UserSubscription.objects.get(user=request.user)
            is_active = subscription.active and subscription.end_date > timezone.now()
            return Response({
                "is_active": is_active,
                "plan": subscription.plan.name if is_active else None,
                "ends_on": subscription.end_date if is_active else None
            })
        except UserSubscription.DoesNotExist:
            return Response({"is_active": False})
        
class PremiumOnlyView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSubscription]

    def get(self, request):
        return Response({"message": "Welcome to premium content!"})
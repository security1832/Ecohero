from ..models import *
from rest_framework import serializers #type:ignore

class SubscriptionPlanSeriaizer(serializers.Modelserializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class UserSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSubscription
        fields = '__all__'
        read_only_fields = ['user', 'start_date', 'end_date', 'active']
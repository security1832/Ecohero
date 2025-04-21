from rest_framework import serializers # type: ignore
from ..models import *

class ChallengeSerializer(serializers.ModelsSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'

class UserChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserChallenge
        fields = ['id', 'user', 'challenge', 'is_completed', 'completed_at']
        read_only_fields = ['completed_at']    
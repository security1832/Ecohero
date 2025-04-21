from django.shortcuts import render
from rest_framework import generics, permissions, status # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from django.utils.timezone import now
from ..models import *
from .serializers import *
from users.models import UserProfile, UserBadge

# Create your views here.
class ChallengeListCreateView(APIView):
    permissions_classes = [permissions.IsAuthenticatedOrReadOnly]
    def get(self, request):
        challenges = Challenge.objects.all()
        serializer = ChallengeSerializer(challenges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = ChallengeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TakeChallengeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UserChallengeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CompleteChallengeView(APIView):
    permissions_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        challenge_id = request.data.get('chalenge_id')
        user = request.user

        if not challenge_id:
            return Response({'error': 'Challenge name required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_challenge = UserChallenge.objects.get(user=user, challenge_id=challenge_id)

            if user_challenge.is_completed:
                return Response({'detail': 'Challenge already completed'}, status=status.HTTP_200_OK)
            
            user_challenge.is_completed = True
            user_challenge.completed_at = now()
            user_challenge.save()

            challenge_xp = user_challenge.challenge.xp_reward
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.total_xp_earned += challenge_xp

            BADGE_THRESHOLDS = {
                100: 'Bronze',
                250: 'Silver',
                500: 'Gold',
            }

            for threshold, badge_name in sorted(BADGE_THRESHOLDS.items()):
                if user_profile.total_xp >= threshold:
                    user_profile.badge = badge_name
            
            return Response({'message': 'Challenge completed suceessfully'}, status=status.HTTP_200_OK)
        
        except UserChallenge.DoesNotExist:
            return Response({'error': 'Challenge not found'}, status=status.HTTP_404_NOT_FOUND)
    


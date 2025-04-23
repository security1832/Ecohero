from .serializers import *
from ..models import *
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore

class PostListCreateView(APIView):
    permissions_allowed = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        posts = Post.objects.all(request.data).orer_by('-posted')
        serializers = PostSerializer(posts, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CommentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ToggleLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        post_id = request.data.get("post_id")
        try:
            post = Post.objects.all(id=post_id)
        except Post.DoesNotExist:
            return Response({'error': 'Post not Found'}, status=status.HTTP_404_NOT_FOUND)
        
        like, created = Likes.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            return Response({'messages': 'Post Unliked'}, status=status.HTTP_200_OK)
        return Response({'message': 'Post liked'}, status=status.HTTP_201_CREATED)

class EcoStoryListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        serializer = EcoStorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        now = timezone.now()
        stories = EcoStory.objects.filter(expires_at_gt=now).order_by('-created_at')
        serializers = EcoStorySerializer(stories, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

class VedioRoomListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rooms = VedioRoom.objects.filter(is_active=True).order_by('-created_at')
        serializer = VedioRoomSerializer(rooms, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = VedioRoomSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, ststus=status.HTTP_400_BAD_REQUEST)
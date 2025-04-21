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
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
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


from .serializers import *
from ..models import *
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from django.shortcuts import get_object_or_404

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
    
class ChatRoomView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rooms = ChatRoom.objects.filter(participants=request.user)
        serializer = ChatRoomSerializer(rooms, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ChatRoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save()
            room.participant.add(request.user)

            if room.room_type == 'public':
                room.participants.add(*User.objects.all())

            return Response(ChatRoomSerializer(room).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_METHOD)

class MessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, room_id):
        room = ChatRoom.objects.get(id=room_id)
        if request.user not in room.participants.all() and room.room_type !='public':
            return Response({'error' : 'Not a member of the group'}, status=403)
        data = request.data.copy()
        data['sender']= request.user.id
        data['room'] = room_id
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def get(self, request, room_id):
        room = ChatRoom.objects.get(id=room_id)
        if request.user not in room.participants.all() and room.room_type != 'public':
            return Response({'error': 'Not a Member'}, status=403)
        messages = room.messages.order_by('timestamp')
        return Response(MessageSerializer(messages, many=True).data)

class NotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        notification_id = request.data.get('id')
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'}) 

class MessageSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.GET.get('q', '')
        room_id = request.GET.get('room', None)

        if not query:
            return Response({"detail": "Query parameter `q` is required."}, status=400)

        messages = Message.objects.filter(
            Q(content__icontains=query),
            Q(room__participants=request.user)
        )

        if room_id:
            messages = messages.filter(room_id=room_id)

        messages = messages.order_by('-timestamp')[:50]  # limit for performance
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
# community/views.py

class ChatRoomAdminView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, room_id):
        action = request.data.get('action')
        target_user_id = request.data.get('user_id')
        room = get_object_or_404(ChatRoom, id=room_id)

        if not room.is_admin(request.user):
            return Response({"detail": "You are not an admin of this room."}, status=403)

        if action == 'add_participant':
            room.participants.add(target_user_id)
        elif action == 'remove_participant':
            room.participants.remove(target_user_id)
        elif action == 'make_admin':
            room.admins.add(target_user_id)
        elif action == 'remove_admin':
            room.admins.remove(target_user_id)
        elif action == 'rename':
            room.name = request.data.get('new_name', room.name)
            room.save()
        elif action == 'delete':
            room.delete()
            return Response({"detail": "Room deleted."}, status=204)
        else:
            return Response({"detail": "Invalid action."}, status=400)

        return Response({"detail": "Action completed successfully."})

    
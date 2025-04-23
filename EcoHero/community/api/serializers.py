from rest_framework import serializers # type: ignore
from ..models import *

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields ='__all__'

class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
class EcoStorySerializer(serializers.ModelSerializer):
    class Mete:
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class VedioRoomSerializer(serializers.ModelSerializer):
    jitsi_url = serializers.ReadOnlyFields()

    class Meta:
        model = VedioRoom
        fields = ['id', 'name', 'creator', 'created_at', 'is_active', 'jitsi_url']

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_username', 'content', 'timestamp', 'room']

class ChatRoomSerializer(serializers.ModelsSerializer):
    participants = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    admin = serializers.StringRelatedField(many=True)
    messages = MessageSerializer(many=True, read_only=True)
    room_type = serializers.ChoiceField(choices=ChatRoom.ROOM_TYPES)
    name = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'admins', 'participants', 'room_type', 'name', 'description', 'messages', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'message', 'chat_room', 'content', 'is_read', 'created_at']

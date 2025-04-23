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
from django.urls import path
from .views import *

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('comments/', CommentCreateView.as_view(), name='comment-create'),
    path('posts/like/', ToggleLikeView.as_view(), name='toggle-like'),

    path('stories/', EcoStoryListCreateView.as_view(), name='stories'),

    path('chat-rooms/', ChatRoomView.as_view(), name='chat_rooms'),
    path('chat-rooms/<int:room_id>/messages/', MessageView.as_view(), name='room_messages'),
    path('chatrooms/<int:room_id>/admin/', ChatRoomAdminView.as_view(), name='chatroom_admin'),
    path('notifications/', NotificationView.as_view(), name='notifications'),

    path('messages/search/', MessageSearchView.as_view(), name='message_search'),
]
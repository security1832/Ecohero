from django.urls import path
from .views import *

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('comments/', CommentCreateView.as_view(), name='comment-create'),
    path('posts/like/', ToggleLikeView.as_view(), name='toggle-like'),
]
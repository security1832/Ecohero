from django.urls import path
from .views import *

urlpatterns = [
    path('challenges/', ChallengeListCreateView.as_view(), name='challenges'),
    path('take-challenge/', TakeChallengeView.as_view(), name='start'),
    path('complete/', CompleteChallengeView.as_view(), name='complete'),
    path('create/', ChallengeListCreateView, name='create')
]
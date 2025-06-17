# chats/urls.py
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from .views import ConversationViewSet, MessageViewSet, delete_user
from django.urls import path, include

# Base router for conversations
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversations')

# Nested router for messages under conversations
conversations_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
    path('delete-account/', delete_user, name='delete_user'),
]

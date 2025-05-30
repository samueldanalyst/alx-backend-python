from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from chats.views import ConversationViewSet, MessageViewSet

# Main router
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversations')

# Nested router for messages under conversations
nested_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
nested_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include(nested_router.urls)),
    path('api-auth/', include('rest_framework.urls')),  # ✅ Fixes the warning
]

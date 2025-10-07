from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from .views import ConversationViewSet, MessageViewSet, UserViewSet

# Create the main router
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Create nested router for messages within conversations
conversations_router = nested_routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

app_name = 'chats'

urlpatterns = [
    # Main API endpoints
    path('api/', include(router.urls)),
    # Nested endpoints for messages within conversations
    path('api/', include(conversations_router.urls)),
    # Authentication endpoints
    path('api/auth/', include('rest_framework.urls')),
]
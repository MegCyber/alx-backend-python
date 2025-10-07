# chats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from . import auth

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'messages', views.MessageViewSet, basename='message')

# The API URLs are now determined automatically by the router
app_name = 'chats'

urlpatterns = [
    # Include all the router URLs
    path('', include(router.urls)),
    
    # JWT Authentication endpoints
    path('auth/register/', auth.register_user, name='auth-register'),
    path('auth/login/', auth.login_user, name='auth-login'),
    path('auth/logout/', auth.logout_user, name='auth-logout'),
    path('auth/token/', auth.CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/me/', auth.get_current_user, name='current-user'),
]

"""
This will create the following URL patterns:

Users:
- GET    /api/users/                    # List all users
- POST   /api/users/                    # Create new user
- GET    /api/users/{id}/               # Get specific user
- PUT    /api/users/{id}/               # Update user
- PATCH  /api/users/{id}/               # Partial update user
- DELETE /api/users/{id}/               # Delete user
- GET    /api/users/me/                 # Get current user profile
- GET    /api/users/{id}/conversations/ # Get user's conversations

Conversations:
- GET    /api/conversations/                      # List user's conversations
- POST   /api/conversations/                      # Create new conversation
- GET    /api/conversations/{id}/                 # Get specific conversation
- PUT    /api/conversations/{id}/                 # Update conversation
- PATCH  /api/conversations/{id}/                 # Partial update conversation
- DELETE /api/conversations/{id}/                 # Delete conversation
- GET    /api/conversations/{id}/messages/        # Get conversation messages
- POST   /api/conversations/{id}/add_participant/ # Add participant
- POST   /api/conversations/{id}/remove_participant/ # Remove participant
- POST   /api/conversations/{id}/mark_as_read/    # Mark messages as read

Messages:
- GET    /api/messages/               # List accessible messages
- POST   /api/messages/               # Send new message
- GET    /api/messages/{id}/          # Get specific message
- PUT    /api/messages/{id}/          # Update message
- PATCH  /api/messages/{id}/          # Partial update message
- DELETE /api/messages/{id}/          # Delete message
- POST   /api/messages/{id}/mark_as_read/ # Mark message as read
- GET    /api/messages/search/?q=text     # Search messages

Authentication:
- POST   /api/auth/login/             # Login and get token
"""
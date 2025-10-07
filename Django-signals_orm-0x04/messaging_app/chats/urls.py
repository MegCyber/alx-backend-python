from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    # Inbox view (cached)
    path('inbox/', views.inbox, name='inbox'),
    
    # Conversation detail (cached)
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    
    # Threaded conversation view
    path('thread/<int:message_id>/', views.threaded_conversation, name='threaded_conversation'),
    
    # Mark message as read
    path('message/<int:message_id>/read/', views.mark_as_read, name='mark_as_read'),
    
    # Message edit history
    path('message/<int:message_id>/history/', views.message_history, name='message_history'),
    
    # Delete user account
    path('account/delete/', views.delete_user, name='delete_user'),
]
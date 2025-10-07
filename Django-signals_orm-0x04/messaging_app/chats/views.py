from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch
from django.contrib.auth.models import User
from messaging.models import Message, Notification


# Task 2: View for deleting user account
@login_required
def delete_user(request):
    """
    Allow a user to delete their own account.
    All related data will be cleaned up via signals.
    """
    if request.method == 'POST':
        user = request.user
        username = user.username
        
        # Log out the user before deletion
        from django.contrib.auth import logout
        logout(request)
        
        # Delete the user (signals will handle cleanup)
        user.delete()
        
        # Redirect to home page with success message
        django_messages.success(
            request, 
            f"Account {username} has been successfully deleted."
        )
        return redirect('admin:index')
    
    # Show confirmation page
    return render(request, 'chats/confirm_delete_user.html')


# Task 5: Cached view for displaying conversation messages
@cache_page(60)  # Cache for 60 seconds
@login_required
def conversation_detail(request, conversation_id):
    """
    Display all messages in a conversation.
    Uses caching to reduce database load for frequently accessed conversations.
    Optimized with select_related and prefetch_related.
    """
    # Get the conversation starter message
    conversation = get_object_or_404(Message, id=conversation_id)
    
    # Fetch all messages in the thread with optimizations
    messages = Message.objects.filter(
        parent_message=conversation
    ).select_related(
        'sender', 'receiver'
    ).prefetch_related(
        Prefetch('replies', queryset=Message.objects.select_related('sender'))
    ).order_by('timestamp')
    
    context = {
        'conversation': conversation,
        'messages': messages,
    }
    
    return render(request, 'chats/conversation_detail.html', context)


# Additional view: List all conversations (also cached)
@cache_page(60)  # Cache for 60 seconds
@login_required
def inbox(request):
    """
    Display user's inbox with all received messages.
    Uses custom manager to show unread messages first.
    """
    # Get unread messages using custom manager
    unread_messages = Message.unread.unread_for_user(request.user)
    
    # Get all messages for the user
    all_messages = Message.objects.filter(
        receiver=request.user
    ).select_related(
        'sender'
    ).order_by('-timestamp')
    
    context = {
        'unread_messages': unread_messages,
        'all_messages': all_messages,
        'unread_count': unread_messages.count(),
    }
    
    return render(request, 'chats/inbox.html', context)


@login_required
def mark_as_read(request, message_id):
    """
    Mark a message as read.
    """
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    message.read = True
    message.save()
    
    return redirect('chats:inbox')


# Task 3: View for threaded conversations
@login_required
def threaded_conversation(request, message_id):
    """
    Display a message and all its replies in a threaded format.
    Uses recursive querying and ORM optimizations.
    """
    # Get the parent message
    parent_message = get_object_or_404(Message, id=message_id)
    
    # Get all replies recursively using prefetch_related
    replies = Message.objects.filter(
        parent_message=parent_message
    ).select_related(
        'sender', 'receiver'
    ).prefetch_related(
        'replies__sender',
        'replies__receiver'
    )
    
    context = {
        'parent_message': parent_message,
        'replies': replies,
    }
    
    return render(request, 'chats/threaded_conversation.html', context)


@login_required
def message_history(request, message_id):
    """
    Display the edit history of a message.
    """
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user has permission to view this message
    if request.user not in [message.sender, message.receiver]:
        django_messages.error(request, "You don't have permission to view this message.")
        return redirect('chats:inbox')
    
    # Get message history
    history = message.history.all()
    
    context = {
        'message': message,
        'history': history,
    }
    
    return render(request, 'chats/message_history.html', context)
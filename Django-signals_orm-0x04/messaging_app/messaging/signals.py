from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory


# Task 0: Signal for User Notifications
@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """
    Automatically create a notification when a new message is sent.
    Triggered after a Message instance is saved.
    """
    if created:
        # Create notification for the receiver
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type='new_message',
            content=f"You have a new message from {instance.sender.username}"
        )
        
        # If it's a reply to another message, notify the parent message sender
        if instance.parent_message:
            Notification.objects.create(
                user=instance.parent_message.sender,
                message=instance,
                notification_type='message_reply',
                content=f"{instance.sender.username} replied to your message"
            )


# Task 1: Signal for Logging Message Edits
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Log the old content of a message before it's updated.
    Creates a MessageHistory entry with the previous content.
    """
    if instance.pk:  # Only for existing messages (not new ones)
        try:
            # Get the old version of the message from the database
            old_message = Message.objects.get(pk=instance.pk)
            
            # Check if content has changed
            if old_message.content != instance.content:
                # Create history entry with old content
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content
                )
                
                # Mark message as edited
                instance.edited = True
                
                # Optionally notify the receiver about the edit
                Notification.objects.create(
                    user=instance.receiver,
                    message=instance,
                    notification_type='message_edit',
                    content=f"{instance.sender.username} edited their message"
                )
        except Message.DoesNotExist:
            # Message doesn't exist yet, skip logging
            pass


# Task 2: Signal for Deleting User-Related Data
@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Clean up all related data when a user is deleted.
    Deletes messages, notifications, and message histories.
    
    Note: If CASCADE is set on foreign keys, Django handles this automatically.
    This signal is useful for custom cleanup logic or logging.
    """
    # Delete all messages sent by the user
    Message.objects.filter(sender=instance).delete()
    
    # Delete all messages received by the user
    Message.objects.filter(receiver=instance).delete()
    
    # Delete all notifications for the user
    Notification.objects.filter(user=instance).delete()
    
    # Note: MessageHistory entries will be deleted via CASCADE
    # when their related Message is deleted
    
    # Optional: Log the deletion
    print(f"Deleted all data related to user: {instance.username}")

# Note: Ensure that the signals are imported in the AppConfig's ready() method
# to ensure they are registered when the app is loaded. 
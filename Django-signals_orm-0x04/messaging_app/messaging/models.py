from django.db import models
from django.contrib.auth.models import User


class UnreadMessagesManager(models.Manager):
    """Custom manager to filter unread messages for a specific user."""
    
    def unread_for_user(self, user):
        """Return only unread messages for the specified user."""
        return self.filter(receiver=user, read=False).only(
            'id', 'sender', 'content', 'timestamp'
        )


class Message(models.Model):
    """
    Model representing a message between users.
    Supports threading via parent_message field.
    """
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    
    # Self-referential foreign key for threaded conversations
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    
    # Default manager
    objects = models.Manager()
    
    # Custom manager for unread messages
    unread = UnreadMessagesManager()
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['receiver', 'read']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
    
    def get_thread(self):
        """
        Retrieve all replies to this message recursively.
        Uses select_related and prefetch_related for optimization.
        """
        return Message.objects.filter(
            parent_message=self
        ).select_related(
            'sender', 'receiver'
        ).prefetch_related('replies')


class MessageHistory(models.Model):
    """
    Model to store edit history of messages.
    Tracks old content before edits.
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = 'Message histories'
    
    def __str__(self):
        return f"History for Message {self.message.id} at {self.edited_at}"


class Notification(models.Model):
    """
    Model to store user notifications.
    Linked to User and Message models.
    """
    NOTIFICATION_TYPES = (
        ('new_message', 'New Message'),
        ('message_edit', 'Message Edited'),
        ('message_reply', 'Message Reply'),
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='new_message'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.notification_type}"
    
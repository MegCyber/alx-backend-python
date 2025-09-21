# chats/models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Extended User model with additional fields"""
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    
    user_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        db_index=True
    )
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(unique=True, blank=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='guest'
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    # Remove username requirement since we're using email
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'chats_user'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Conversation(models.Model):
    """Model for conversations between users"""
    conversation_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        db_index=True
    )
    participants = models.ManyToManyField(
        User, 
        related_name='conversations',
        through='ConversationParticipant'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chats_conversation'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['-updated_at']),
        ]
    
    def __str__(self):
        participant_names = ", ".join([
            participant.full_name for participant in self.participants.all()[:3]
        ])
        if self.participants.count() > 3:
            participant_names += f" and {self.participants.count() - 3} others"
        return f"Conversation: {participant_names}"
    
    @property
    def last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.first()
    
    @property
    def participant_count(self):
        """Get the number of participants in this conversation"""
        return self.participants.count()


class ConversationParticipant(models.Model):
    """Through model for conversation participants"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(default=timezone.now)
    is_admin = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'chats_conversation_participants'
        unique_together = ['user', 'conversation']
    
    def __str__(self):
        return f"{self.user.full_name} in {self.conversation.conversation_id}"


class Message(models.Model):
    """Model for messages in conversations"""
    message_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        db_index=True
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE,
        related_name='messages'
    )
    message_body = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'chats_message'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
            models.Index(fields=['-sent_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.full_name} at {self.sent_at}"
    
    def save(self, *args, **kwargs):
        """Update conversation's updated_at when a message is saved"""
        super().save(*args, **kwargs)
        # Update the conversation's updated_at timestamp
        self.conversation.updated_at = self.sent_at
        self.conversation.save(update_fields=['updated_at'])


class MessageRead(models.Model):
    """Track which users have read which messages"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_by')
    read_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'chats_message_read'
        unique_together = ['user', 'message']
    
    def __str__(self):
        return f"{self.user.full_name} read message {self.message.message_id}"
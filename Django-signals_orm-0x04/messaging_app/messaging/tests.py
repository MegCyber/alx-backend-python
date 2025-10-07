from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory


class SignalTestCase(TestCase):
    """Test cases for Django signals in the messaging app."""
    
    def setUp(self):
        """Set up test users."""
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='testpass123'
        )
    
    def test_notification_created_on_new_message(self):
        """Test that a notification is created when a new message is sent."""
        # Create a new message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello Bob!"
        )
        
        # Check that a notification was created for the receiver
        notification = Notification.objects.filter(
            user=self.user2,
            message=message,
            notification_type='new_message'
        )
        
        self.assertEqual(notification.count(), 1)
        self.assertIn(self.user1.username, notification.first().content)
    
    def test_message_edit_logged(self):
        """Test that message edits are logged in MessageHistory."""
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        # Edit the message
        message.content = "Edited content"
        message.save()
        
        # Check that history was created
        history = MessageHistory.objects.filter(message=message)
        self.assertEqual(history.count(), 1)
        self.assertEqual(history.first().old_content, "Original content")
        self.assertTrue(message.edited)
    
    def test_user_deletion_cascades(self):
        """Test that user deletion removes related data."""
        # Create messages and notifications
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
        
        # Verify notification exists
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 1)
        
        # Delete user2
        self.user2.delete()
        
        # Verify related data is deleted
        self.assertEqual(
            Message.objects.filter(receiver=self.user2).count(), 
            0
        )
        self.assertEqual(
            Notification.objects.filter(user=self.user2).count(), 
            0
        )
    
    def test_threaded_conversation(self):
        """Test threaded conversations with parent messages."""
        # Create parent message
        parent = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Parent message"
        )
        
        # Create reply
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply message",
            parent_message=parent
        )
        
        # Check that parent notification and reply notification are created
        notifications = Notification.objects.filter(user=self.user1)
        self.assertEqual(notifications.count(), 1)
        
        # Verify reply notification exists
        reply_notification = notifications.filter(
            notification_type='message_reply'
        )
        self.assertEqual(reply_notification.count(), 1)
    
    def test_unread_messages_manager(self):
        """Test custom UnreadMessagesManager."""
        # Create messages
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread message 1",
            read=False
        )
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Read message",
            read=True
        )
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread message 2",
            read=False
        )
        
        # Get unread messages
        unread = Message.unread.unread_for_user(self.user2)
        
        # Should only return 2 unread messages
        self.assertEqual(unread.count(), 2)
        
        # Verify all returned messages are unread
        for message in unread:
            self.assertFalse(message.read)

from django.contrib import admin
from .models import Message, Notification, MessageHistory

admin.site.register(Message)
admin.site.register(Notification)
admin.site.register(MessageHistory) 

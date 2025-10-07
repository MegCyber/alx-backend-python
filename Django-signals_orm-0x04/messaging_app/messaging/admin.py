from django.contrib import admin
from .models import Message, Notification, MessageHistory


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""
    list_display = [
        'id', 
        'sender', 
        'receiver', 
        'content_preview', 
        'timestamp', 
        'edited', 
        'read',
        'parent_message'
    ]
    list_filter = ['edited', 'read', 'timestamp']
    search_fields = ['sender__username', 'receiver__username', 'content']
    readonly_fields = ['timestamp']
    raw_id_fields = ['sender', 'receiver', 'parent_message']
    
    def content_preview(self, obj):
        """Show a preview of message content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    
    content_preview.short_description = 'Content'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""
    list_display = [
        'id', 
        'user', 
        'notification_type', 
        'content_preview', 
        'timestamp', 
        'is_read'
    ]
    list_filter = ['notification_type', 'is_read', 'timestamp']
    search_fields = ['user__username', 'content']
    readonly_fields = ['timestamp']
    raw_id_fields = ['user', 'message']
    
    def content_preview(self, obj):
        """Show a preview of notification content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    
    content_preview.short_description = 'Content'


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    """Admin interface for MessageHistory model."""
    list_display = [
        'id', 
        'message', 
        'old_content_preview', 
        'edited_at'
    ]
    list_filter = ['edited_at']
    search_fields = ['old_content', 'message__content']
    readonly_fields = ['edited_at']
    raw_id_fields = ['message']
    
    def old_content_preview(self, obj):
        """Show a preview of old content."""
        return obj.old_content[:50] + '...' if len(obj.old_content) > 50 else obj.old_content
    
    old_content_preview.short_description = 'Old Content'
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Conversation, Message


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for custom User model.
    """
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'date_of_birth')
        }),
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Admin configuration for Conversation model.
    """
    list_display = ['conversation_id', 'get_participants', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['participants__username', 'participants__email']
    filter_horizontal = ['participants']
    readonly_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for Message model.
    """
    list_display = ['message_id', 'sender', 'conversation', 'message_body_preview', 'sent_at']
    list_filter = ['sent_at', 'sender']
    search_fields = ['message_body', 'sender__username', 'conversation__conversation_id']
    readonly_fields = ['message_id', 'sent_at']
    
    def message_body_preview(self, obj):
        return obj.message_body[:50] + "..." if len(obj.message_body) > 50 else obj.message_body
    message_body_preview.short_description = 'Message Preview'
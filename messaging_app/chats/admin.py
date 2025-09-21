# chats/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Conversation, Message, ConversationParticipant, MessageRead


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin interface"""
    list_display = ['email', 'full_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    # Fields for editing user
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    
    # Fields for adding new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'last_login']


class ConversationParticipantInline(admin.TabularInline):
    """Inline for managing conversation participants"""
    model = ConversationParticipant
    extra = 1
    fields = ['user', 'joined_at', 'is_admin']
    readonly_fields = ['joined_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Conversation admin interface"""
    list_display = ['conversation_id', 'participant_list', 'message_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['participants__email', 'participants__first_name', 'participants__last_name']
    readonly_fields = ['conversation_id', 'created_at', 'updated_at']
    inlines = [ConversationParticipantInline]
    
    def participant_list(self, obj):
        """Display list of participants"""
        participants = obj.participants.all()[:3]
        names = [p.full_name for p in participants]
        if obj.participants.count() > 3:
            names.append(f"and {obj.participants.count() - 3} others")
        return ", ".join(names)
    participant_list.short_description = "Participants"
    
    def message_count(self, obj):
        """Display number of messages in conversation"""
        count = obj.messages.count()
        return format_html('<strong>{}</strong>', count)
    message_count.short_description = "Messages"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Message admin interface"""
    list_display = ['message_id', 'sender', 'conversation_short', 'message_preview', 'sent_at', 'is_read']
    list_filter = ['sent_at', 'is_read', 'sender__role']
    search_fields = ['message_body', 'sender__email', 'sender__first_name', 'sender__last_name']
    readonly_fields = ['message_id', 'sent_at']
    date_hierarchy = 'sent_at'
    
    def conversation_short(self, obj):
        """Display shortened conversation info"""
        participants = obj.conversation.participants.all()[:2]
        names = [p.full_name for p in participants]
        if obj.conversation.participants.count() > 2:
            names.append("...")
        return f"Conv: {', '.join(names)}"
    conversation_short.short_description = "Conversation"
    
    def message_preview(self, obj):
        """Display message preview"""
        preview = obj.message_body[:50]
        if len(obj.message_body) > 50:
            preview += "..."
        return preview
    message_preview.short_description = "Message Preview"


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    """Conversation participant admin interface"""
    list_display = ['user', 'conversation_id', 'joined_at', 'is_admin']
    list_filter = ['is_admin', 'joined_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['joined_at']


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    """Message read status admin interface"""
    list_display = ['user', 'message_preview', 'read_at']
    list_filter = ['read_at']
    search_fields = ['user__email', 'message__message_body']
    readonly_fields = ['read_at']
    
    def message_preview(self, obj):
        """Display message preview"""
        preview = obj.message.message_body[:30]
        if len(obj.message.message_body) > 30:
            preview += "..."
        return preview
    message_preview.short_description = "Message"


# Customize admin site headers
admin.site.site_header = "Messaging App Administration"
admin.site.site_title = "Messaging App Admin"
admin.site.index_title = "Welcome to Messaging App Administration"
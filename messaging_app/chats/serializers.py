# chats/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Conversation, Message, ConversationParticipant, MessageRead


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'user_id', 'first_name', 'last_name', 'full_name', 
            'email', 'phone_number', 'role', 'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 
            'role', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'sender_id', 'conversation', 
            'message_body', 'sent_at', 'is_read'
        ]
        read_only_fields = ['message_id', 'sent_at']
    
    def create(self, validated_data):
        # Set sender from request user if not provided
        if 'sender_id' not in validated_data:
            validated_data['sender'] = self.context['request'].user
        else:
            validated_data['sender_id'] = validated_data.pop('sender_id')
        return super().create(validated_data)


class MessageCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating messages"""
    
    class Meta:
        model = Message
        fields = ['conversation', 'message_body']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ConversationParticipantSerializer(serializers.ModelSerializer):
    """Serializer for conversation participants"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ConversationParticipant
        fields = ['user', 'joined_at', 'is_admin']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model"""
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    last_message = MessageSerializer(read_only=True)
    participant_count = serializers.ReadOnlyField()
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_ids',
            'last_message', 'participant_count', 'messages',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create()
        
        # Add current user as participant and admin
        current_user = self.context['request'].user
        ConversationParticipant.objects.create(
            user=current_user,
            conversation=conversation,
            is_admin=True
        )
        
        # Add other participants
        for participant_id in participant_ids:
            try:
                user = User.objects.get(user_id=participant_id)
                ConversationParticipant.objects.get_or_create(
                    user=user,
                    conversation=conversation,
                    defaults={'is_admin': False}
                )
            except User.DoesNotExist:
                continue
        
        return conversation


class ConversationDetailSerializer(ConversationSerializer):
    """Detailed serializer for individual conversations"""
    messages = serializers.SerializerMethodField()
    participants_detail = ConversationParticipantSerializer(
        source='conversationparticipant_set', 
        many=True, 
        read_only=True
    )
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['participants_detail']
    
    def get_messages(self, obj):
        # Get recent messages (limit to prevent large payloads)
        recent_messages = obj.messages.all()[:50]
        return MessageSerializer(recent_messages, many=True).data


class ConversationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for conversation lists"""
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'last_message', 
            'unread_count', 'updated_at'
        ]
    
    def get_last_message(self, obj):
        last_message = obj.messages.first()
        if last_message:
            return {
                'message_id': last_message.message_id,
                'sender': last_message.sender.full_name,
                'message_body': last_message.message_body[:100] + '...' if len(last_message.message_body) > 100 else last_message.message_body,
                'sent_at': last_message.sent_at
            }
        return None
    
    def get_unread_count(self, obj):
        user = self.context['request'].user
        # Count messages not read by current user
        return obj.messages.exclude(
            read_by__user=user
        ).count()
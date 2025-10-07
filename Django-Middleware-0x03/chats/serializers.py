from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'date_of_birth', 'created_at']
        read_only_fields = ['user_id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'sender_id', 'conversation', 
                 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']

    def create(self, validated_data):
        # Set sender to the current user if not provided
        if 'sender_id' not in validated_data:
            validated_data['sender'] = self.context['request'].user
        else:
            validated_data['sender_id'] = validated_data.pop('sender_id')
        return super().create(validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model.
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'participant_ids', 
                 'messages', 'last_message', 'created_at', 'updated_at']
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        """
        Get the last message in the conversation.
        """
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        
        # Add current user as participant
        conversation.participants.add(self.context['request'].user)
        
        # Add other participants
        if participant_ids:
            for participant_id in participant_ids:
                try:
                    user = User.objects.get(user_id=participant_id)
                    conversation.participants.add(user)
                except User.DoesNotExist:
                    pass
        
        return conversation
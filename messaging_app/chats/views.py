from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and managing conversations.
    Provides endpoints for creating conversations and managing participants.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_at']
    search_fields = ['participants__username', 'participants__email']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        """
        Filter conversations to only include those where the current user is a participant.
        """
        return Conversation.objects.filter(participants=self.request.user).prefetch_related('participants', 'messages')

    def perform_create(self, serializer):
        """
        Create a new conversation with the current user as a participant.
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """
        Add a participant to an existing conversation.
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            return Response({'status': 'participant added'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from an existing conversation.
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.remove(user)
            return Response({'status': 'participant removed'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and managing messages within conversations.
    Provides endpoints for sending messages to existing conversations.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['conversation', 'sender', 'sent_at']
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['sent_at']
    ordering = ['sent_at']

    def get_queryset(self):
        """
        Filter messages to only include those from conversations where the current user is a participant.
        """
        user_conversations = Conversation.objects.filter(participants=self.request.user)
        return Message.objects.filter(conversation__in=user_conversations).select_related('sender', 'conversation')

    def perform_create(self, serializer):
        """
        Create a new message with the current user as the sender.
        """
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def by_conversation(self, request):
        """
        Get all messages for a specific conversation.
        """
        conversation_id = request.query_params.get('conversation_id')
        if not conversation_id:
            return Response({'error': 'conversation_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            conversation = Conversation.objects.get(
                conversation_id=conversation_id,
                participants=request.user
            )
            messages = self.get_queryset().filter(conversation=conversation)
            serializer = self.get_serializer(messages, many=True)
            return Response(serializer.data)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found or access denied'}, 
                          status=status.HTTP_404_NOT_FOUND)
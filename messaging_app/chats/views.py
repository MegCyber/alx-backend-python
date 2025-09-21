# chats/views.py
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

from .models import User, Conversation, Message, ConversationParticipant, MessageRead
from .serializers import (
    UserSerializer, UserCreateSerializer, ConversationSerializer,
    ConversationDetailSerializer, ConversationListSerializer,
    MessageSerializer, MessageCreateSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users"""
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        # Allow filtering by role or search by name/email
        role = self.request.query_params.get('role')
        search = self.request.query_params.get('search')
        
        if role:
            queryset = queryset.filter(role=role)
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('first_name', 'last_name')
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def conversations(self, request, pk=None):
        """Get all conversations for a specific user"""
        user = self.get_object()
        conversations = user.conversations.all()
        serializer = ConversationListSerializer(
            conversations, 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversations"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only return conversations where current user is a participant
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            'participants',
            Prefetch('messages', queryset=Message.objects.select_related('sender'))
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        """Create a new conversation"""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to the conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            participant, created = ConversationParticipant.objects.get_or_create(
                user=user,
                conversation=conversation,
                defaults={'is_admin': False}
            )
            
            if created:
                return Response(
                    {'message': f'{user.full_name} added to conversation'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'message': f'{user.full_name} is already in this conversation'},
                    status=status.HTTP_200_OK
                )
        
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """Remove a participant from the conversation"""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            participant = ConversationParticipant.objects.get(
                user=user,
                conversation=conversation
            )
            participant.delete()
            
            return Response(
                {'message': f'{user.full_name} removed from conversation'},
                status=status.HTTP_200_OK
            )
        
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except ConversationParticipant.DoesNotExist:
            return Response(
                {'error': 'User is not a participant in this conversation'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a specific conversation"""
        conversation = self.get_object()
        messages = conversation.messages.select_related('sender').all()
        
        # Pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark all messages in conversation as read by current user"""
        conversation = self.get_object()
        user = request.user
        
        # Get all unread messages in this conversation
        unread_messages = conversation.messages.exclude(
            read_by__user=user
        )
        
        # Mark them as read
        for message in unread_messages:
            MessageRead.objects.get_or_create(
                user=user,
                message=message
            )
        
        return Response(
            {'message': f'Marked {unread_messages.count()} messages as read'},
            status=status.HTTP_200_OK
        )


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing messages"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only return messages from conversations where user is a participant
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation').distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        """Create a new message"""
        message = serializer.save()
        
        # Automatically mark message as read by sender
        MessageRead.objects.create(
            user=self.request.user,
            message=message
        )
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a specific message as read"""
        message = self.get_object()
        user = request.user
        
        read_record, created = MessageRead.objects.get_or_create(
            user=user,
            message=message
        )
        
        if created:
            return Response(
                {'message': 'Message marked as read'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'message': 'Message already marked as read'},
                status=status.HTTP_200_OK
            )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search messages by content"""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {'error': 'Query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = self.get_queryset().filter(
            message_body__icontains=query
        )
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


# Additional utility views
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

class AuthTokenView(APIView):
    """Custom authentication endpoint"""
    permission_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=email, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
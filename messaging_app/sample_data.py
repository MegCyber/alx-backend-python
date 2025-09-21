# sample_data.py
# Run this script to populate the database with sample data
# Usage: python manage.py shell < sample_data.py

from chats.models import User, Conversation, Message, ConversationParticipant
from django.utils import timezone
import uuid

print("Creating sample data for messaging app...")

# Create sample users
users_data = [
    {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone_number': '+1234567890',
        'role': 'guest'
    },
    {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane@example.com',
        'phone_number': '+1234567891',
        'role': 'host'
    },
    {
        'first_name': 'Bob',
        'last_name': 'Johnson',
        'email': 'bob@example.com',
        'phone_number': '+1234567892',
        'role': 'guest'
    },
    {
        'first_name': 'Alice',
        'last_name': 'Williams',
        'email': 'alice@example.com',
        'phone_number': '+1234567893',
        'role': 'admin'
    },
    {
        'first_name': 'Charlie',
        'last_name': 'Brown',
        'email': 'charlie@example.com',
        'phone_number': '+1234567894',
        'role': 'host'
    }
]

# Create users
created_users = []
for user_data in users_data:
    user, created = User.objects.get_or_create(
        email=user_data['email'],
        defaults={
            **user_data,
            'password': 'pbkdf2_sha256$600000$dummy$hash'  # Dummy password hash
        }
    )
    if created:
        user.set_password('password123')  # Set actual password
        user.save()
        print(f"Created user: {user.full_name}")
    else:
        print(f"User already exists: {user.full_name}")
    created_users.append(user)

# Create sample conversations
john, jane, bob, alice, charlie = created_users

# Conversation 1: John and Jane
conv1 = Conversation.objects.create()
ConversationParticipant.objects.create(user=john, conversation=conv1, is_admin=True)
ConversationParticipant.objects.create(user=jane, conversation=conv1)

# Conversation 2: Group chat with Bob, Alice, and Charlie
conv2 = Conversation.objects.create()
ConversationParticipant.objects.create(user=bob, conversation=conv2, is_admin=True)
ConversationParticipant.objects.create(user=alice, conversation=conv2)
ConversationParticipant.objects.create(user=charlie, conversation=conv2)

# Conversation 3: John and Bob
conv3 = Conversation.objects.create()
ConversationParticipant.objects.create(user=john, conversation=conv3, is_admin=True)
ConversationParticipant.objects.create(user=bob, conversation=conv3)

print(f"Created {Conversation.objects.count()} conversations")

# Create sample messages
messages_data = [
    # Conversation 1 messages
    {
        'conversation': conv1,
        'sender': john,
        'message_body': "Hi Jane! How are you doing today?",
        'sent_at': timezone.now() - timezone.timedelta(hours=2)
    },
    {
        'conversation': conv1,
        'sender': jane,
        'message_body': "Hey John! I'm doing great, thanks for asking. How about you?",
        'sent_at': timezone.now() - timezone.timedelta(hours=1, minutes=55)
    },
    {
        'conversation': conv1,
        'sender': john,
        'message_body': "I'm doing well too! Are you free for lunch this weekend?",
        'sent_at': timezone.now() - timezone.timedelta(hours=1, minutes=50)
    },
    {
        'conversation': conv1,
        'sender': jane,
        'message_body': "That sounds great! I'd love to catch up. What time works for you?",
        'sent_at': timezone.now() - timezone.timedelta(hours=1, minutes=45)
    },
    
    # Conversation 2 messages (group chat)
    {
        'conversation': conv2,
        'sender': bob,
        'message_body': "Hey everyone! Welcome to our project group chat.",
        'sent_at': timezone.now() - timezone.timedelta(hours=3)
    },
    {
        'conversation': conv2,
        'sender': alice,
        'message_body': "Thanks for creating this, Bob! This will make coordination much easier.",
        'sent_at': timezone.now() - timezone.timedelta(hours=2, minutes=58)
    },
    {
        'conversation': conv2,
        'sender': charlie,
        'message_body': "Agreed! When should we schedule our first team meeting?",
        'sent_at': timezone.now() - timezone.timedelta(hours=2, minutes=55)
    },
    {
        'conversation': conv2,
        'sender': bob,
        'message_body': "How about tomorrow at 2 PM? We can meet in the conference room.",
        'sent_at': timezone.now() - timezone.timedelta(hours=2, minutes=50)
    },
    {
        'conversation': conv2,
        'sender': alice,
        'message_body': "Perfect! I'll send out calendar invites to everyone.",
        'sent_at': timezone.now() - timezone.timedelta(hours=2, minutes=45)
    },
    
    # Conversation 3 messages
    {
        'conversation': conv3,
        'sender': john,
        'message_body': "Bob, did you see the latest project updates?",
        'sent_at': timezone.now() - timezone.timedelta(minutes=30)
    },
    {
        'conversation': conv3,
        'sender': bob,
        'message_body': "Yes, I just reviewed them. The timeline looks good!",
        'sent_at': timezone.now() - timezone.timedelta(minutes=25)
    },
    {
        'conversation': conv3,
        'sender': john,
        'message_body': "Great! Let me know if you need any help with the implementation.",
        'sent_at': timezone.now() - timezone.timedelta(minutes=20)
    }
]

# Create messages
for msg_data in messages_data:
    message = Message.objects.create(**msg_data)
    print(f"Created message: {message.message_body[:30]}...")

print(f"\nSample data created successfully!")
print(f"Users: {User.objects.count()}")
print(f"Conversations: {Conversation.objects.count()}")
print(f"Messages: {Message.objects.count()}")
print(f"Participants: {ConversationParticipant.objects.count()}")

print("\nSample user credentials:")
print("Email: john@example.com, Password: password123")
print("Email: jane@example.com, Password: password123")
print("Email: bob@example.com, Password: password123")
print("Email: alice@example.com, Password: password123")
print("Email: charlie@example.com, Password: password123")
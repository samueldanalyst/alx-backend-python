from rest_framework import serializers
from .models import CustomUser, Message, Conversation

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['user_id', 'email', 'first_name', 'last_name', 'phone_number']



class MessageSerializer(serializers.ModelSerializer):
    sender = CustomUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'conversation', 'content', 'timestamp', 'is_read']



class ConversationSerializer(serializers.ModelSerializer):
    participants = CustomUserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at', 'messages']

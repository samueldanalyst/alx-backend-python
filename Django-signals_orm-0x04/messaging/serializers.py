from rest_framework import serializers
from .models import CustomUser, Message, Conversation

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['user_id', 'email', 'first_name', 'last_name', 'phone_number']


class RecursiveMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    receiver = serializers.UUIDField(source='receiver.user_id', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_name',
            'receiver',
            'receiver_name',
            'content',
            'timestamp',
            'parent_message',
            'replies',
        ]

    def get_sender_name(self, obj):
        return f"{obj.sender.first_name} {obj.sender.last_name}"

    def get_receiver_name(self, obj):
        if obj.receiver:
            return f"{obj.receiver.first_name} {obj.receiver.last_name}"
        return None

    def get_replies(self, obj):
        replies_qs = obj.replies.all().select_related('sender', 'receiver')
        return RecursiveMessageSerializer(replies_qs, many=True).data


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    receiver = serializers.UUIDField(source='receiver.user_id', read_only=True)
    parent_message = serializers.PrimaryKeyRelatedField(
        queryset=Message.objects.all(),
        required=False,
        allow_null=True
    )
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_name',
            'receiver',
            'receiver_name',
            'content',
            'timestamp',
            'parent_message',
            'replies',
        ]

    def get_sender_name(self, obj):
        return f"{obj.sender.first_name} {obj.sender.last_name}"

    def get_receiver_name(self, obj):
        if obj.receiver:
            return f"{obj.receiver.first_name} {obj.receiver.last_name}"
        return None

    def get_replies(self, obj):
        replies_qs = obj.replies.all().select_related('sender', 'receiver')
        return RecursiveMessageSerializer(replies_qs, many=True).data

    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    participants = CustomUserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at', 'messages']

    def get_messages(self, obj):
        # Only top-level messages (no parent)
        top_level_messages = obj.messages.filter(parent_message__isnull=True).select_related(
            'sender', 'receiver'
        ).prefetch_related(
            'replies__sender', 'replies__receiver', 'replies__replies'
        )
        return MessageSerializer(top_level_messages, many=True).data
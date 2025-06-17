
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

from django.db.models import Prefetch
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .pagination import MessageResultsSetPagination
from .permission import IsParticipantOfConversation
from .filters import MessageFilter
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_messages(request):
    user = request.user
    unread_qs = Message.unread.for_user(user)
    serializer = MessageSerializer(unread_qs, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    user = request.user
    user.delete()
    return Response({"detail": "User account and related data deleted."}, status=status.HTTP_204_NO_CONTENT)





class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # ✅ Return only conversations the user is part of
        return Conversation.objects.filter(participants=self.request.user)

    def get_object(self):
        # ✅ Ensure object-level permissions are checked
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        conversation_id = kwargs.get('pk')

        # ✅ Optimize query with select_related and prefetch_related for replies
        try:
            conversation = Conversation.objects.prefetch_related(
                Prefetch(
                    'messages',
                    queryset=Message.objects.filter(parent_message__isnull=True)  # Top-level messages only
                        .select_related('sender', 'receiver', 'parent_message')
                        .prefetch_related('replies')  # replies = related_name in Message model
                )
            ).get(pk=conversation_id)
        except Conversation.DoesNotExist:
            return Response({'error': 'Conversation not found.'}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, conversation)
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Send a message to an existing conversation.
        Supports replying to a specific message using 'parent_message'.
        Requires 'conversation' and 'content' in request data.
        """
        conversation_id = request.data.get('conversation')
        content = request.data.get('content')
        parent_message_id = request.data.get('parent_message')  # Optional for replies

        if not conversation_id or not content:
            return Response({"error": "Both conversation and content are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(pk=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # Ensure sender is a participant
        if request.user not in conversation.participants.all():
            return Response({"error": "You are not a participant in this conversation."},
                            status=status.HTTP_403_FORBIDDEN)

        # Automatically find the receiver
        participants = conversation.participants.exclude(user_id=request.user.user_id)
        receiver = participants.first() if participants.exists() else None

        if not receiver:
            return Response({"error": "Receiver could not be determined."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Handle parent_message if it's a reply
        parent_message = None
        if parent_message_id:
            try:
                parent_message = Message.objects.get(message_id=parent_message_id)
            except Message.DoesNotExist:
                return Response({"error": "Parent message not found."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Optional: Ensure parent_message belongs to same conversation
            if parent_message.conversation_id != conversation_id:
                return Response({"error": "Parent message does not belong to this conversation."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Create the message
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            conversation=conversation,
            content=content,
            parent_message=parent_message  # Can be None
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter]
    pagination_class = MessageResultsSetPagination
    filterset_class = MessageFilter

    def get_queryset(self):
        # ✅ Only return messages where the request.user is a participant
        return Message.objects.filter(conversation__participants=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """
        Edit a message.
        Only the sender of the message can edit it.
        The 'content' field must be provided.
        """
        message = self.get_object()

        # ✅ Ensure only the sender can edit
        if message.sender != request.user:
            return Response({"detail": "You can only edit your own messages."},
                            status=status.HTTP_403_FORBIDDEN)

        new_content = request.data.get("content")
        if not new_content:
            return Response({"error": "Content is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        message.content = new_content
        message.save()  # ✅ This triggers the pre_save signal to log history
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def create(self, request, *args, **kwargs):
        """
        Send a message to an existing conversation.
        Requires 'conversation' (conversation_id) and 'content' in request data.
        The sender is set to the logged-in user.
        """
        conversation_id = request.data.get('conversation')
        content = request.data.get('content')
        parent_message_id = request.data.get('parent_message')

        if not conversation_id or not content:
            return Response({"error": "Both conversation and content are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(pk=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found."},
                            status=status.HTTP_404_NOT_FOUND)

        
        # ✅ Automatically find the receiver from participants
        participants = conversation.participants.all()
        receiver = [user for user in participants if user != request.user]
        receiver = receiver[0] if receiver else None  # Fallback to avoid index error

        if not receiver:
            return Response({"error": "Receiver could not be determined."},
                            status=status.HTTP_400_BAD_REQUEST)

        # ✅ Now create message with receiver set
        parent_message = None
        if parent_message_id:
            try:
                parent_message = Message.objects.get(pk=parent_message_id)
            except Message.DoesNotExist:
                return Response({"error": "Parent message not found."},
                                status=status.HTTP_400_BAD_REQUEST)

        # ✅ Create the message with parent_message
            message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            conversation=conversation,
            content=content,
            parent_message=parent_message  # ✅ INCLUDE THIS
        )


        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    

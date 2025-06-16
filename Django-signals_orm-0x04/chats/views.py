
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .pagination import MessageResultsSetPagination
from .permission import IsParticipantOfConversation
from .filters import MessageFilter














class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    
    def create(self, request, *args, **kwargs):
        participants = request.data.get('participants', [])
        if not participants or not isinstance(participants, list):
            return Response({"error": "Participants list is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Add requesting user if not included
        user_id = request.user.user_id
        if user_id not in participants:
            participants.append(user_id)

        # Validate that all participants exist
        User = get_user_model()
        valid_users = User.objects.filter(user_id__in=participants).values_list('user_id', flat=True)
        if set(participants) != set(valid_users):
            return Response({"error": "One or more participant IDs are invalid."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if conversation with same participants already exists
        existing_conversations = Conversation.objects.all()
        for conv in existing_conversations:
            conv_participants = set(conv.participants.values_list('user_id', flat=True))
            if conv_participants == set(participants):
                serializer = self.get_serializer(conv)
                return Response(serializer.data, status=status.HTTP_200_OK)

        # Create new conversation
        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        conversation.save()

        serializer = self.get_serializer(conversation)
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

    def create(self, request, *args, **kwargs):
        """
        Send a message to an existing conversation.
        Requires 'conversation' (conversation_id) and 'content' in request data.
        The sender is set to the logged-in user.
        """
        conversation_id = request.data.get('conversation')
        content = request.data.get('content')

        if not conversation_id or not content:
            return Response({"error": "Both conversation and content are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(pk=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # ✅ Check if the requesting user is a participant
        if request.user not in conversation.participants.all():
            return Response({"detail": "You are not a participant of this conversation."},
                            status=status.HTTP_403_FORBIDDEN)

        message = Message.objects.create(
            sender=request.user,
            conversation=conversation,
            content=content
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

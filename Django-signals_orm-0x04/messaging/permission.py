
from rest_framework import permissions






class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access messages.
    """

    def has_permission(self, request, view):
        # Allow only authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        obj can be a Message or a Conversation depending on the ViewSet.
        We check if the requesting user is a participant of the conversation.
        """
        # If the object is a Message, get its conversation
        conversation = getattr(obj, 'conversation', obj)

        return request.user in conversation.participants.all()

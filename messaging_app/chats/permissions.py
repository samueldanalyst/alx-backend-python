from rest_framework import permissions

class IsParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """

    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants.all()

class IsSender(permissions.BasePermission):
    """
    Custom permission to only allow senders of a message to access it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user

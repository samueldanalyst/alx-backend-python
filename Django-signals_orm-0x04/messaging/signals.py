# chats/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory

@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    if created and instance.receiver:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if not instance.pk:
        return  # Skip new messages (they don’t have an old version yet)

    try:
        old_instance = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    if old_instance.content != instance.content:
        # ✅ Log the previous version
        MessageHistory.objects.create(
            message=old_instance,
            content=old_instance.content,
        )
        # ✅ Flag the message as edited
        instance.edited = True  # This will be saved when the message is saved

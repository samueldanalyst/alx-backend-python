from django.contrib import admin


from .models import Conversation, Message, CustomUser, Notification, MessageHistory


admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(CustomUser)
admin.site.register(Notification)
admin.site.register(MessageHistory)

# Register your models here.

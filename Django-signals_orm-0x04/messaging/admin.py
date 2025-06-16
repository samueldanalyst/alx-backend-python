from django.contrib import admin


from .models import Conversation, Message, CustomUser, Notification


admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(CustomUser)
admin.site.register(Notification)

# Register your models here.

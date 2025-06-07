from django.contrib import admin


from .models import Conversation, Message, CustomUser


admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(CustomUser)

# Register your models here.

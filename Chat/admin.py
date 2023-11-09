from django.contrib import admin
from .models import Profile, UserInfo, ChatInfo, ChatMessage

admin.site.register(Profile)
admin.site.register(UserInfo)
admin.site.register(ChatInfo)
admin.site.register(ChatMessage)
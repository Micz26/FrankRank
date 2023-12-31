from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.db import models
from django.contrib.auth.models import User
import bcrypt

User = get_user_model()


# Models
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    email = models.EmailField(unique=True)
    openai_api_key = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.email = self.email
        self.openai_api_key = self.openai_api_key
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.id_user


class UserInfo(models.Model):
    id_user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    investments = models.CharField(max_length=255, blank=True, null=True)
    sectors = models.CharField(max_length=255, blank=True, null=True)
    risk_level = models.CharField(max_length=255, blank=True, null=True)
    expected_annual_return = models.CharField(max_length=255, blank=True, null=True)
    investment_period = models.CharField(max_length=255, blank=True, null=True)
    esg = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(UserInfo, self).save(*args, **kwargs)


class ChatInfo(models.Model):
    id_chat = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.CharField(max_length=100)
    name_chat = models.TextField(default="New Chat")
    category = models.CharField(max_length=45, default="Personal Finance")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(ChatInfo, self).save(*args, **kwargs)


class ChatMessage(models.Model):
    id_chat = models.ForeignKey(ChatInfo, on_delete=models.CASCADE)
    prompt = models.TextField()
    response = models.TextField()
    image = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super(ChatMessage, self).save(*args, **kwargs)

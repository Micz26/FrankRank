from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.db import models
from django.contrib.auth.models import User
import bcrypt

User = get_user_model()

# Hash maila
def hash_email(email):
    hashed_email = bcrypt.hashpw(email.encode('utf-8'), bcrypt.gensalt())
    return hashed_email.decode('utf-8')

# Hash open ai api key
def hash_api_key(api_key):
    hashed_key = bcrypt.hashpw(api_key.encode('utf-8'), bcrypt.gensalt())
    return hashed_key.decode('utf-8')


# Models
class Profile(models.Model):
    id_user = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    email = models.EmailField(unique=True)
    openai_api_key = models.CharField(max_length=255)

    investments = models.CharField(max_length=255, blank=True, null=True)
    sectors = models.CharField(max_length=255, blank=True, null=True)
    risk_level = models.CharField(max_length=255, blank=True, null=True)
    expected_annual_return = models.CharField(max_length=255, blank=True, null=True)
    investment_period = models.CharField(max_length=255, blank=True, null=True)
    esg = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.email = hash_email(self.email)
        self.openai_api_key = hash_api_key(self.openai_api_key)
        super(Profile, self).save(*args, **kwargs)
    def __str__(self):
        return self.user.username
    
    
class ChatInfo(models.Model):
    id_user = models.IntegerField()
    chat = models.TextField()
    category = models.CharField(max_length=45, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(ChatInfo, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.id_user
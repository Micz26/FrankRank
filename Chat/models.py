from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.db import models
from django.contrib.auth.models import User
import bcrypt

User = get_user_model()

# Hash mail
def hash_email(email):
    hashed_email = bcrypt.hashpw(email.encode('utf-8'), bcrypt.gensalt())
    return hashed_email.decode('utf-8')

# Hash open ai api key
def hash_api_key(api_key):
    hashed_key = bcrypt.hashpw(api_key.encode('utf-8'), bcrypt.gensalt())
    return hashed_key.decode('utf-8')


# Models
class InvesmentsProfile(models.Model):    
    investments = models.CharField(max_length=255, blank=True, null=True)
    sectors = models.CharField(max_length=255, blank=True, null=True)
    risk_level = models.CharField(max_length=255, blank=True, null=True)
    expected_annual_return = models.CharField(max_length=255, blank=True, null=True)
    investment_period = models.CharField(max_length=255, blank=True, null=True)
    esg = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.email = hash_email(self.email)
        self.openai_api_key = hash_api_key(self.openai_api_key)
        super(InvesmentsProfile, self).save(*args, **kwargs)
    def __str__(self):
        return self.user.username
    
    
class ChatInfo(models.Model):
    id_user = models.IntegerField()
    id_chat = models.IntegerField()
    chat = models.TextField()
    category = models.CharField(max_length=45, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(ChatInfo, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.id_user
 
class User(models.Model):
    id_user = models.IntegerField(primary_key = True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firtsName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    birthday = models.DateField()
    email = models.EmailField(unique=True)
    openai_api_key = models.CharField(max_length=255)
    
    def save(self, *args, **kwargs):
        self.email = hash_email(self.email)
        self.openai_api_key = hash_api_key(self.openai_api_key)
        super(User, self).save(*args, **kwargs)
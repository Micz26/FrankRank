# Generated by Django 4.2.6 on 2023-11-25 16:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatInfo',
            fields=[
                ('id_chat', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user', models.CharField(max_length=100)),
                ('name_chat', models.TextField(default='New Chat')),
                ('category', models.CharField(default='Personal Finance', max_length=45)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_user', models.IntegerField()),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('openai_api_key', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('investments', models.CharField(blank=True, max_length=255, null=True)),
                ('sectors', models.CharField(blank=True, max_length=255, null=True)),
                ('risk_level', models.CharField(blank=True, max_length=255, null=True)),
                ('expected_annual_return', models.CharField(blank=True, max_length=255, null=True)),
                ('investment_period', models.CharField(blank=True, max_length=255, null=True)),
                ('esg', models.CharField(blank=True, max_length=255, null=True)),
                ('id_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Chat.profile')),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField()),
                ('response', models.TextField()),
                ('image', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('id_chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Chat.chatinfo')),
            ],
        ),
    ]

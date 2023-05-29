# Generated by Django 4.2.1 on 2023-05-25 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0002_remove_conversation_messages_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='vocation',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]

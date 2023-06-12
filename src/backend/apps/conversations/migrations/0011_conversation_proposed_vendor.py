# Generated by Django 4.2.1 on 2023-06-12 01:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0010_alter_conversation_last_viewed'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='proposed_vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proposed_for_conversation', to='conversations.vendor'),
        ),
    ]
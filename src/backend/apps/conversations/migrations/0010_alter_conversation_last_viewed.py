# Generated by Django 4.2.1 on 2023-06-11 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0009_conversation_last_viewed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='last_viewed',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

# Generated by Django 4.2.1 on 2023-07-25 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='agreeToTerms',
            field=models.BooleanField(default=False),
        ),
    ]
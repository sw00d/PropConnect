# Generated by Django 4.2.1 on 2023-08-13 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0014_vendor_has_opted_in_vendor_is_archived_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='address',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='point_of_contact_has_interjected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='conversation',
            name='tenant_intro_message',
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='vendor_intro_message',
            field=models.CharField(blank=True, max_length=800, null=True),
        ),
        migrations.AddField(
            model_name='conversation',
            name='waiting_on_property_manager',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='error_on_send',
            field=models.BooleanField(default=False),
        ),
    ]

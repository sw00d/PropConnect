# Generated by Django 4.2.1 on 2023-06-14 00:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_company_payment_method'),
        ('users', '0002_user_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='users', to='companies.company'),
        ),
    ]
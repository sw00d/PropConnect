# Generated by Django 4.2.1 on 2023-06-15 21:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_rename_street_company_street_1_company_street_2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='street_2',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]

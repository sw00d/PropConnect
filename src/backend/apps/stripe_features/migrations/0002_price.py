# Generated by Django 4.2.1 on 2023-06-20 01:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_features', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_price_id', models.CharField(max_length=200, unique=True)),
                ('unit_amount', models.IntegerField(help_text='The price of the product in cents.')),
                ('currency', models.CharField(default='USD', help_text='Three-letter ISO currency code.', max_length=3)),
                ('recurring', models.BooleanField(default=True, help_text="True if the price is recurring, False if it's a one-time price.")),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='stripe_features.product')),
            ],
        ),
    ]
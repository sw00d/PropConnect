from django.db import models


class Product(models.Model):
    stripe_product_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Price(models.Model):
    stripe_price_id = models.CharField(max_length=200, unique=True)
    product = models.ForeignKey(Product, related_name='prices', on_delete=models.CASCADE)
    unit_amount = models.IntegerField(help_text="The price of the product in cents.")
    currency = models.CharField(max_length=3, default="USD", help_text="Three-letter ISO currency code.")
    recurring = models.BooleanField(default=True, help_text="True if the price is recurring, False if it's a one-time price.")

    def __str__(self):
        return f"{self.unit_amount} {self.currency} ({'recurring' if self.recurring else 'one-time'})"

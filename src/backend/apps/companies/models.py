from django.db import models
from djstripe.models import PaymentMethod


class Company(models.Model):
    DOOR_CHOICES = [
        (1, '1-50'),
        (2, '50-200'),
        (3, '200-500'),
        (4, '500-1000'),
        (5, '1000-10,000'),
        (6, '10,000+'),
    ]
    name = models.CharField(max_length=200)
    website = models.CharField(max_length=200)  # Validation can be done on FE and serializer.
    number_of_doors = models.IntegerField(choices=DOOR_CHOICES)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)

    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

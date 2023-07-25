import stripe
from django.db import models
from djstripe.models import Subscription


class Company(models.Model):
    DOOR_CHOICES = [
        ('1-50', '1-50'),
        ('50-200', '50-200'),
        ('200-500', '200-500'),
        ('500-1000', '500-1000'),
        ('1000-10,000', '1000-10,000'),
        ('10,000+', '10,000+'),
    ]
    name = models.CharField(max_length=200)
    website = models.CharField(max_length=200, blank=True)  # Validation can be done on FE and serializer instead of urlfield
    number_of_doors = models.CharField(max_length=16, choices=DOOR_CHOICES)

    current_subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    customer_stripe_id = models.CharField(max_length=50, blank=True, null=True, unique=True)

    street_1 = models.CharField(max_length=200)
    street_2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    assistant_phone_number = models.CharField(max_length=20, blank=True, null=True)

    @property
    def has_active_subscription(self):
        if self.current_subscription:
            return self.current_subscription.status == 'active'
        return False


class Transaction(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    charge_date = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)
    invoice_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f"Transaction for {self.company.name} - {'Successful' if self.successful else 'Failed'}"

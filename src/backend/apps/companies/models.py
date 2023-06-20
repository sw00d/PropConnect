import stripe
from django.db import models


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

    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    street_1 = models.CharField(max_length=200)
    street_2 = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    @property
    def check_subscription(self):
        if self.stripe_subscription_id:
            subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
            return subscription.status == 'active'
        return False

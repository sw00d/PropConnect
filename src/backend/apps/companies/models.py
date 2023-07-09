import stripe
from django.db import models
from djstripe.models import Subscription, Customer


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

    stripe_customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    current_subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)

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
            return self.current_subscription['status'] == 'active'
        return False

    # @property
    # def current_subscription(self):
    #     if self.current_subscription_id:
    #         subscription = stripe.Subscription.retrieve(self.current_subscription_id)
    #         return subscription
    #     return None

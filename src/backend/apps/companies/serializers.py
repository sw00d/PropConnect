# serializers.py

from rest_framework import serializers

from settings.base import STRIPE_SECRET_KEY
from .models import Company

from djstripe.models import Customer, PaymentMethod
import stripe

stripe.api_key = STRIPE_SECRET_KEY


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['billing_details']


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'name',
            'website',
            'number_of_doors',
            'street_1',
            'street_2',
            'city',
            'state',
            'zip_code',
            'country'
        )

    def create(self, validated_data):
        # pop payment_method_id if not necessary for company creation
        validated_data.pop('payment_method_id', None)
        company = super().create(validated_data)

        # get user from request
        user = self.context.get("request").user
        # assign company to user
        user.company = company
        user.save()

        return company


class CompanyUpdateSerializer(serializers.ModelSerializer):
    payment_method_id = serializers.CharField(write_only=True)

    class Meta:
        model = Company
        fields = (
            'name',
            'number_of_doors',
            'street_1',
            'street_2',
            'city',
            'state',
            'zip_code',
            'country',
            'payment_method_id'  # stripe payment method id
        )

    def update(self, instance, validated_data):

        payment_method_id = validated_data.pop('payment_method_id')
        # Create Stripe customer
        stripe_customer = stripe.Customer.create(
            payment_method=payment_method_id,  # payment method ID from your frontend
            email=instance.users.all().first().email,  # company admin's email
            name=instance.name,  # company's name
            invoice_settings={
                'default_payment_method': payment_method_id,
            },
        )

        # Sync customer with dj-stripe
        customer, created = Customer.get_or_create(subscriber=instance.users.all().first())
        customer.api_retrieve()  # Sync customer data with Stripe
        print(stripe.Customer.retrieve(stripe_customer.id))
        customer.default_payment_method = PaymentMethod.sync_from_stripe_data(
            stripe.Customer.retrieve(stripe_customer.id).invoice_settings.default_payment_method
        )
        customer.save()
        # Save Stripe customer ID in Company model
        instance.stripe_customer_id = stripe_customer.id
        instance.save()

        return instance

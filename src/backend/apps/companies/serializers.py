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
        payment_method_id = validated_data.pop('payment_method_id', None)

        # call super update
        instance = super().update(instance, validated_data)

        if payment_method_id:
            try:
                # Create Stripe customer
                stripe_customer = stripe.Customer.create(
                    payment_method=payment_method_id,
                    email=instance.users.first().email,
                    name=instance.name,
                    invoice_settings={
                        'default_payment_method': payment_method_id,
                    },
                )
            except stripe.error.StripeError as e:
                # Handle Stripe errors here
                raise serializers.ValidationError(f"Stripe error: {e}")

            try:
                # Sync customer with dj-stripe
                customer, created = Customer.get_or_create(subscriber=instance.users.first())
                customer.api_retrieve()

                # Avoid an unnecessary API call by using the data from stripe_customer
                customer.default_payment_method = PaymentMethod.sync_from_stripe_data(
                    stripe_customer.invoice_settings.default_payment_method
                )
                customer.save()
            except Exception as e:  # Replace with a more specific exception if possible
                # Handle other errors here
                raise serializers.ValidationError(f"Error updating customer: {e}")

                # Save Stripe customer ID in Company model
            instance.stripe_customer_id = stripe_customer.id
            instance.save()

        return instance
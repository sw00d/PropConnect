"""Use this file to make factories for the project.

https://factoryboy.readthedocs.io/en/latest/recipes.html
"""
import string
import random

import factory

from django.contrib.auth import get_user_model

from companies.models import Company
from conversations.models import Tenant, Conversation, PhoneNumber, Vendor
from djstripe.models import Subscription, Customer
from datetime import timedelta
from django.utils import timezone


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    class Meta:
        model = get_user_model()

    @factory.post_generation
    def password(self, created, extracted):
        if not created:
            return
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password('factoryuserpass')
        self.save()


class TenantFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    number = factory.Faker('numerify', text="+1##########")
    address = factory.Faker('address')

    class Meta:
        model = Tenant


class VendorFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    number = factory.Faker('numerify', text="+1##########")

    class Meta:
        model = Vendor


class TwilioNumberFactory(factory.django.DjangoModelFactory):
    # Assuming `number` is a field in TwilioNumber model
    number = "+12085558828"
    # most_recent_conversation = ConversationFactory()

    class Meta:
        model = PhoneNumber


def generate_random_string(length=10):
    """Generate a random string of fixed length """
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choices(letters_and_digits, k=length))


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    id = factory.LazyFunction(lambda: f"fake-customer-{generate_random_string()}")
    # ... add any other needed fields ...


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    id = factory.LazyFunction(lambda: f"fake-subscription-{generate_random_string()}")
    current_period_end = (timezone.now() + timedelta(days=30)).isoformat()  # 30 days from now, in UNIX timestamp format
    current_period_start = timezone.now().isoformat()
    customer = factory.SubFactory(CustomerFactory)
    status = "active"


class CompanyFactory(factory.django.DjangoModelFactory):
    number_of_doors = factory.Faker('random_int', min=1, max=100)

    # by default, set the stripe IDs to some fake IDs
    current_subscription = factory.SubFactory(SubscriptionFactory)
    point_of_contact = factory.SubFactory(UserFactory)

    class Meta:
        model = Company

    @factory.lazy_attribute
    def name(self):
        return f"Test Company"


class ConversationFactory(factory.django.DjangoModelFactory):
    tenant = factory.SubFactory(TenantFactory)
    vendor = factory.SubFactory(VendorFactory)
    company = factory.SubFactory(CompanyFactory)
    is_active = factory.Faker('boolean')
    last_viewed = factory.Faker('past_datetime', start_date="-30d", tzinfo=None)
    date_created = factory.Faker('past_datetime', start_date="-30d", tzinfo=None)

    class Meta:
        model = Conversation


# class PaymentMethodFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = PaymentMethod
#
#     # Here, the required fields for PaymentMethod are added.
#     # Replace with the correct values as per your implementation.
#     billing_details = factory.Dict({
#         'name': factory.Faker('name'),
#         'email': factory.Faker('email'),
#         'phone': factory.Faker('phone_number'),
#         'address': factory.Dict({
#             'line1': factory.Faker('street_name'),
#             'line2': factory.Faker('secondary_address'),
#             'city': factory.Faker('city'),
#             'state': factory.Faker('state_abbr'),
#             'postal_code': factory.Faker('zipcode'),
#             'country': factory.Faker('country_code')
#         })
#     })



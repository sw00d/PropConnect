"""Use this file to make factories for the project.

https://factoryboy.readthedocs.io/en/latest/recipes.html
"""
import factory

from django.contrib.auth import get_user_model

from conversations.models import Tenant, Conversation, PhoneNumber


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
        model = Tenant


class TwilioNumberFactory(factory.django.DjangoModelFactory):
    # Assuming `number` is a field in TwilioNumber model
    number = "+12085558828"
    most_recent_conversation = factory.PostGenerationMethodCall('save')

    class Meta:
        model = PhoneNumber


class ConversationFactory(factory.django.DjangoModelFactory):
    tenant = factory.SubFactory(TenantFactory)
    vendor = factory.SubFactory(VendorFactory)
    is_active = factory.Faker('boolean')
    last_viewed = factory.Faker('past_datetime', start_date="-30d", tzinfo=None)
    twilio_number = factory.SubFactory(TwilioNumberFactory)

    class Meta:
        model = Conversation


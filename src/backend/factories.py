"""Use this file to make factories for the project.

https://factoryboy.readthedocs.io/en/latest/recipes.html
"""
import factory

from django.contrib.auth import get_user_model

from conversations.models import Tenant


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

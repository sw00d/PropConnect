from datetime import datetime, timedelta

import stripe
from django.utils.timezone import now
from random import randint

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from twilio.rest import Client

from conversations.models import Vendor, PhoneNumber, Tenant, Conversation, Message
from factories import TenantFactory
from settings.base import DEFAULT_TWILIO_NUMBER, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, STRIPE_SECRET_KEY
from stripe_features.models import Product, Price

User = get_user_model()

stripe.api_key = STRIPE_SECRET_KEY

# make generate_vendors have an optional arugment

def generate_vendors(company=None):
    vendor_data = {
        "plumber": {
            'name': 'Plumber Sam',
            'number': '+12086608828',
            'keywords': ['leak', 'water', 'drain', 'faucet', 'plumber']
        },
        "electrician": {
            'name': 'Electrician Sam',
            'number': '+12086608828',
            'keywords': ['light', 'outlet', 'circuit', 'power', 'electric', 'electrician']
        },
        "handyman": {
            'name': 'Handyman Sam',
            'number': '+12086608828',
            'keywords': ['door', 'window', 'wall', 'general', 'handyman']
        },
        "appliance specialist": {
            'name': 'Appliance Specialist Sam',
            'number': '+12086608828',
            'keywords': ['fridge', 'oven', 'dishwasher', 'washer', 'dryer', 'appliance']
        },
        "air-condition specialist": {
            'name': 'HVAC Pro Sam',
            'number': '+12086608828',
            'keywords': ['heating', 'cooling', 'ventilation', 'ac', 'furnace', 'hvac']
        },
        "locksmith": {
            'name': 'Locksmith Sam',
            'number': '+12086608828',
            'keywords': ['lock', 'key', 'security', 'door', 'safe', 'locksmith']
        },
        "flooring specialist": {
            'name': 'Flooring Specialist Sam',
            'number': '+12086608828',
            'keywords': ['floor', 'carpet', 'tile', 'wood', 'laminate', 'flooring']
        },
        "painter": {
            'name': 'Painter Sam',
            'number': '+12086608828',
            'keywords': ['paint', 'color', 'wall', 'ceiling', 'interior', 'painter']
        },
        "drywall specialist": {
            'name': 'Drywall Specialist Sam',
            'number': '+12086608828',
            'keywords': ['drywall', 'wallboard', 'plasterboard', 'gypsum', 'sheetrock', 'drywall']
        },
    }

    for vendor, info in vendor_data.items():
        Vendor.objects.get_or_create(
            name=info['name'],
            number=info['number'],
            keywords=info['keywords'],
            vocation=vendor,
            company=company
        )
        print('Made vendor.', vendor)


def get_active_twilio_numbers():
    # Your Account SID and Auth Token from twilio.com/console
    twilio_auth_token = TWILIO_AUTH_TOKEN
    twilio_sid = TWILIO_ACCOUNT_SID

    client = Client(twilio_sid, twilio_auth_token)

    active_numbers = []
    for number in client.incoming_phone_numbers.list():
        if number.status == "in-use":
            active_numbers.append(number.phone_number)

    return active_numbers


def generate_conversations():
    convo_types = [
        # Different cases. Please expand on this when needed.
        "no_vendor_assigned",
        "tenant_to_vendor",
        "inactive",
        "active",
    ]
    days_ago = 3
    for convo_type in convo_types:
        vendor1 = Vendor.objects.first()

        tenant1 = TenantFactory(name=convo_type)
        if convo_type == 'no_vendor_assigned':
            conversation = Conversation.objects.create(tenant=tenant1, is_active=True)
        else:
            conversation = Conversation.objects.create(tenant=tenant1, vendor=vendor1, is_active=True)

        # Create Initial Messages
        Message.objects.create(sender_number="5555555555", receiver_number=DEFAULT_TWILIO_NUMBER, role="user",
                               message_content="Hi. I have a maintenance issue", conversation=conversation)

        Message.objects.create(
            sender_number=DEFAULT_TWILIO_NUMBER, receiver_number="5555555555", role="assistant",
            message_content="Thanks for letting me know! Can you provide your name, address, and a description of the "
                            "issue so I can find the right professional for your situation?",
            conversation=conversation
        )

        Message.objects.create(sender_number="5555555555", receiver_number=DEFAULT_TWILIO_NUMBER, role="user",
                               message_content="My name is Alice. I live at 123 Street. I have a leaky faucet",
                               conversation=conversation

                               )

        Message.objects.create(
            sender_number=DEFAULT_TWILIO_NUMBER, receiver_number="5555555555", role="assistant",
            message_content="Thank you! I think we should send a plumber out to you. I'll put you in touch with our "
                            "preferred plumber and from there you can schedule a time for him to come by your place and "
                            "give it a look.",
            conversation=conversation
        )

        # Vendor Messages
        if convo_type != 'no_vendor_assigned':
            Message.objects.create(
                sender_number=vendor1.number, receiver_number="5555555555", role="assistant",
                message_content="A leaky faucet, huh? When would be a good time for me to come by and take a look?",
                conversation=conversation
            )

            Message.objects.create(
                sender_number="5555555555", receiver_number=vendor1.number, role="user",
                message_content="Tomorrow at 10:30am?", conversation=conversation
            )

            Message.objects.create(
                sender_number=vendor1.number, receiver_number="5555555555", role="assistant",
                message_content="Sounds great! I'll see you then.",
                conversation=conversation
            )

            Message.objects.create(
                sender_number="5555555555", receiver_number=vendor1.number, role="user",
                message_content="Amazing! Thank you!", conversation=conversation
            )

        if convo_type == 'inactive':
            conversation.is_active = False
            conversation.save()

        date_created = now() - timedelta(days=days_ago)
        conversation.date_created = date_created
        conversation.last_viewed = date_created  # all messages of all convos will be unread
        conversation.save()

        # Create PhoneNumbers
        PhoneNumber.objects.create(number="5555555555", most_recent_conversation=conversation, is_base_number=False)

        # update all dates on messages of conversation
        minutes_ago = 10
        for message in conversation.messages.all():
            message.time_sent = now() + timedelta(minutes=minutes_ago)
            message.save()
            # random number between 8 and 30
            minutes_ago += randint(8, 30)
        days_ago += 1


def sync_stripe_product():
    products = stripe.Product.list()

    for product in products:
        # Check if the product already exists in the DB
        db_product = Product.objects.filter(stripe_product_id=product.id).first()
        if not db_product:
            # If not, create a new product
            db_product = Product.objects.create(
                stripe_product_id=product.id,
                name=product.name,
                active=product.active
            )

        # Get the prices associated with this product
        prices = stripe.Price.list(product=product.id)

        for price in prices:
            # Check if the price already exists in the DB
            if not Price.objects.filter(stripe_price_id=price.id).exists():
                # If not, create a new price
                Price.objects.create(
                    stripe_price_id=price.id,
                    product=db_product,
                    unit_amount=price.unit_amount,
                    currency=price.currency,
                    recurring=price.recurring is not None
                    # This is a simple way to check if the price is recurring or not
                )


class Command(BaseCommand):
    help = "Generate data"

    def handle(self, *args, **kwargs):

        # Create stuff here!
        try:
            User.objects.create_superuser('admin@admin.com', 'admin')
            print('Made admin user.')
        except IntegrityError:
            print('Admin user already exists!')

        # TODO Extract these to a separate command so we can run from heroku and whatnot
        # generate_vendors()
        # generate_conversations()
        sync_stripe_product()

        # Loading products from stripe

        for number in get_active_twilio_numbers():
            if number == DEFAULT_TWILIO_NUMBER:
                PhoneNumber.objects.create(number=number, is_base_number=True)
                print('Made base phone.', number)

            else:
                PhoneNumber.objects.create(number=number, is_base_number=False)
                print('Made phone.', number)

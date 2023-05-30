from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from twilio.rest import Client

from conversations.models import Vendor, PhoneNumber, Tenant, Conversation, Message
from settings.base import DEFAULT_TWILIO_NUMBER, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

User = get_user_model()


def generate_vendors():
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
        Vendor.objects.get_or_create(name=info['name'], number=info['number'], keywords=info['keywords'],
                                     vocation=vendor)
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
    vendor1 = Vendor.objects.first()

    tenant1 = Tenant.objects.create(name="Aneesh", number="5555555555", address="123 Street")
    conversation1 = Conversation.objects.create(tenant=tenant1, vendor=vendor1, is_active=True)

    # Create Messages
    Message.objects.create(sender_number="5555555555", receiver_number=DEFAULT_TWILIO_NUMBER, role="user",
                           message_content="Hi. I have a maintenance issue", conversation=conversation1)

    Message.objects.create(
        sender_number=DEFAULT_TWILIO_NUMBER, receiver_number="5555555555", role="assistant",
        message_content="Thanks for letting me know! Can you provide your name, address, and a description of the "
                        "issue so I can find the right professional for your situation?",
        conversation=conversation1
    )

    Message.objects.create(sender_number="5555555555", receiver_number=DEFAULT_TWILIO_NUMBER, role="user",
                           message_content="My name is Alice. I live at 123 Street. I have a leaky faucet",
                           conversation=conversation1

                           )

    Message.objects.create(
        sender_number=DEFAULT_TWILIO_NUMBER, receiver_number="5555555555", role="assistant",
        message_content="Thank you! I think we should send a plumber out to you. I'll put you in touch with our "
                        "preferred plumber and from there you can schedule a time for him to come by your place and "
                        "give it a look.",
        conversation=conversation1
    )

    Message.objects.create(
        sender_number=vendor1.number, receiver_number="5555555555", role="assistant",
        message_content="A leaky faucet, huh? When would be a good time for me to come by and take a look?",
        conversation=conversation1
    )

    Message.objects.create(
        sender_number="5555555555", receiver_number=vendor1.number, role="user",
        message_content="Tomorrow at 10:30am?", conversation=conversation1
    )

    Message.objects.create(
        sender_number=vendor1.number, receiver_number="5555555555", role="assistant",
        message_content="Sounds great! I'll see you then.",
        conversation=conversation1
    )

    Message.objects.create(
        sender_number="5555555555", receiver_number=vendor1.number, role="user",
        message_content="Amazing! Thank you!", conversation=conversation1
    )

    # Create PhoneNumbers
    PhoneNumber.objects.create(number="5555555555", most_recent_conversation=conversation1, is_base_number=False)


class Command(BaseCommand):
    help = "Generate data"

    def handle(self, *args, **kwargs):

        # Create stuff here!

        try:
            User.objects.create_superuser('admin@admin.com', 'admin')
            print('Made admin user.')
        except IntegrityError:
            print('Admin user already exists!')

        generate_vendors()
        generate_conversations()

        for number in get_active_twilio_numbers():
            if number == DEFAULT_TWILIO_NUMBER:
                PhoneNumber.objects.create(number=number, is_base_number=True)
                print('Made base phone.', number)

            else:
                PhoneNumber.objects.create(number=number, is_base_number=False)
                print('Made phone.', number)

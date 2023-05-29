from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from twilio.rest import Client

from conversations.models import Vendor, PhoneNumber
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
        Vendor.objects.get_or_create(name=info['name'], number=info['number'], keywords=info['keywords'], vocation=vendor)
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

        for number in get_active_twilio_numbers():
            if number == DEFAULT_TWILIO_NUMBER:
                PhoneNumber.objects.create(number=number, is_base_number=True)
                print('Made base phone.', number)

            else:
                PhoneNumber.objects.create(number=number, is_base_number=False)
                print('Made phone.', number)


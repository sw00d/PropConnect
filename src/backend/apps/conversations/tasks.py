from datetime import timedelta
from sys import argv

from django.db.models import Q
from django.utils import timezone
from twilio.base.exceptions import TwilioRestException

from settings import celery_app
from .models import Conversation, Message, PhoneNumber, Vendor
from twilio.rest import Client
from settings.base import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, WEBHOOK_URL, TWILIO_TEST_AUTH_TOKEN, \
    TWILIO_TEST_ACCOUNT_SID
import logging
from .utils import error_handler

twilio_auth_token = TWILIO_AUTH_TOKEN
twilio_sid = TWILIO_ACCOUNT_SID
logger = logging.getLogger(__name__)

# TODO Add a task to check how many convos have been started this month and charge 40 cents for conversation. \
#  Task should run on the 1st of every month OR on the renewal date of the company's subscription
# def bill_for_conversations():
#     from companies.models import Company

# TODO Before monthly billing cycle, go through twilio numbers that aren't active and delete them -- something like this:
# def delete_inactive_twilio_numbers():
#     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#     TODO When companys cancel their subscription:
#     TODO 1. Delete the twilio number from the twilio account but keep it in our database so we can buy it later
#     numbers = client.incoming_phone_numbers.list()
#
#     for number in numbers:
#         # Replace `number.is_active` with actual condition or method to check if number is active
#         if number has no active conversations tied to it:
#             client.incoming_phone_numbers(number.sid).delete()


@celery_app.task
def set_old_conversations_to_not_active(hours=48):
    if hours == 0:
        Conversation.objects.filter(is_active=True).update(is_active=False)
    else:
        time_ago = timezone.now() - timedelta(hours=hours)
        old_conversations = Message.objects.filter(time_sent__lt=time_ago).values('conversation').distinct()
        Conversation.objects.filter(id__in=old_conversations, is_active=True).update(is_active=False)


# This is used for the main convo-flow
@celery_app.task
def start_vendor_tenant_conversation(conversation_id, vendor_id):
    from .utils import send_message

    conversation = Conversation.objects.get(id=conversation_id)

    # See if we have any available numbers in twilio and if not, buy one
    available_numbers = PhoneNumber.objects.filter(
        Q(most_recent_conversation__is_active=False) | Q(most_recent_conversation__isnull=True),
        is_base_number=False
    )
    if available_numbers.count() == 0:
        client = Client(twilio_sid, twilio_auth_token)
        number = client.available_phone_numbers("US").local.list(area_code='619')[0]  # TODO This area code should be based off company location
        logger.info(f"Purchasing new number: {number.phone_number}")
        purchase_phone_number_util(number.phone_number)
        conversation_number = PhoneNumber.objects.create(number=number.phone_number, most_recent_conversation=conversation)
    else:
        conversation_number = available_numbers.first()
        logger.info(f"Using existing number: {conversation_number.number} for conversation: {conversation_id}")
        conversation_number.most_recent_conversation = conversation
        conversation_number.save()

    vendor = Vendor.objects.get(id=vendor_id)
    conversation.vendor = vendor
    conversation.save()

    conversation_recap = get_conversation_recap_util(conversation)  # do this before we send the initial vendor message

    message_to_vendor = f"Hey there! I'm a bot for {conversation.company.name}. " \
                        "I have a tenant who is requesting some help. " \
                        "You are now connected with the tenant and can communicate directly with them here."

    send_message(conversation.vendor.number, conversation_number.number, message_to_vendor)
    Message.objects.create(
        message_content=message_to_vendor,
        role="assistant",
        conversation=conversation,
        receiver_number=conversation.vendor.number,
        sender_number=conversation_number.number
    )

    conversation_history = f"Conversation: \n\n {conversation_recap}"
    send_message(conversation.vendor.number, conversation_number.number, conversation_history)
    Message.objects.create(
        message_content=conversation_history,
        role="assistant",
        conversation=conversation,
        receiver_number=conversation.vendor.number,
        sender_number=conversation_number.number
    )

    message_to_tenant = f"Hey there! I'm a bot for {conversation.company.name}. " \
                        f"I've informed the {vendor.vocation}, {vendor.name}, of your situation. " \
                        "You are now connected with the vendor and can communicate directly with them here."
    send_message(conversation.tenant.number, conversation_number.number, message_to_tenant)
    Message.objects.create(
        message_content=message_to_tenant,
        role="assistant",
        conversation=conversation,
        receiver_number=conversation.tenant.number,
        sender_number=conversation_number.number
    )


# This is used for the main convo-flow
def get_conversation_recap_util(conversation):
    string = ''
    messages = conversation.messages.all().order_by('time_sent')
    for message in messages:
        if message.role == 'user':
            string += f"- Tenant: {message.message_content}\n\n"
        elif message.role == 'assistant':
            string += f"- Assistant: {message.message_content}\n\n"

    return string


# def set_sms_url(api_endpoint="/play_the_middle_man/"):
#     # just for testing
#     client = Client(twilio_sid, twilio_auth_token)
#     webhook_url = 'https://propconnect.com' + api_endpoint
#     purchased_number = client.incoming_phone_numbers('PNa433e6bcd35295b2ee942e1b4cc125f2').fetch()
#     address = client.addresses.list(limit=1)[0]
#     print(purchased_number.emergency_address_sid)
#     purchased_number.update(
#         sms_url=webhook_url,
#         address_sid=address.sid,
#         emergency_address_sid=address.sid,
#     )
#     purchased_number = client.incoming_phone_numbers('PNa433e6bcd35295b2ee942e1b4cc125f2').fetch()
#     print(purchased_number.emergency_address_sid)


def purchase_phone_number_util(phone_number, api_endpoint="/play_the_middle_man/", type_of_number='a2p'):
    try:
        if 'pytest' in argv[0]:
            client = Client(TWILIO_TEST_ACCOUNT_SID, TWILIO_TEST_AUTH_TOKEN)
        else:
            client = Client(twilio_sid, twilio_auth_token)

        webhook_url = WEBHOOK_URL + api_endpoint

        if 'pytest' in argv[0]:
            test_client_with_prod_creds = Client(twilio_sid, twilio_auth_token)
            address_sid = test_client_with_prod_creds.addresses.list(limit=1)[0].sid
            webhook_url = 'https://propconnect.io' + api_endpoint
        else:
            address_sid = client.addresses.list(limit=1)[0].sid  # Should eventually be the company's address

        purchased_number = client.incoming_phone_numbers.create(
            phone_number=phone_number,
            sms_url=webhook_url,
            address_sid=address_sid,  # make sure this is being set on purchased numbers
            emergency_address_sid=address_sid  # make sure this is being set on purchased numbers
        )

        if type_of_number == 'a2p':
            # Register a2p number for vendor/tenant coms
            service = client.verify.v2.services.list(limit=1)[0]  # Get first and only service/campaign

            # Here's where we assign the purchased number to the messaging service
            client.proxy.v1 \
                .services(service.sid) \
                .phone_numbers \
                .create(sid=purchased_number.sid)

        if type_of_number == 'toll-free':
            # TODO maybe verify this number in the future?
            pass

        return purchased_number
    except TwilioRestException as e:
        logger.error(f"Failed to purchase phone number. Error: {e}")
        error_handler(e)


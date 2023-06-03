from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from twilio.base.exceptions import TwilioRestException

from settings import celery_app
from .models import Conversation, Message, PhoneNumber, Vendor
from twilio.rest import Client
from settings.base import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, WEBHOOK_URL
import logging

twilio_auth_token = TWILIO_AUTH_TOKEN
twilio_sid = TWILIO_ACCOUNT_SID
logger = logging.getLogger(__name__)


@celery_app.task
def set_old_conversations_to_not_active():
    three_days_ago = timezone.now() - timedelta(days=3)
    old_conversations = Message.objects.filter(time_sent__lt=three_days_ago).values('conversation').distinct()
    Conversation.objects.filter(id__in=old_conversations, is_active=True).update(is_active=False)


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
        number = client.available_phone_numbers("US").local.list(area_code='619')[0]
        print("Purchasing new number:", number.phone_number)
        logger.info(f"Purchasing new number: {number.phone_number}")
        purchase_phone_number_util(number.phone_number)
        conversation_number = PhoneNumber.objects.create(number=number.phone_number,
                                                         most_recent_conversation=conversation)
    else:
        conversation_number = available_numbers.first()
        print("Using existing number:", conversation_number.number)
        conversation_number.most_recent_conversation = conversation
        conversation_number.save()


    vendor = Vendor.objects.get(id=vendor_id)
    conversation.vendor = vendor
    conversation.save()

    conversation_recap = get_conversation_recap_util(conversation)  # do this before we send the initial vendor message

    message_to_vendor = "Hey there! I'm a bot for Home Simple property management. " \
                        "I have a tenant who is requesting some help. " \
                        "Reply here to communicate directly with tenant."

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

    message_to_tenant = "Hey there! I'm a bot for Home Simple property management. " \
                        f"I've informed the {vendor.vocation}, {vendor.name}, of your situation. " \
                        "You can reply directly to this number to communicate with the them."
    send_message(conversation.tenant.number, conversation_number.number, message_to_tenant)
    Message.objects.create(
        message_content=message_to_tenant,
        role="assistant",
        conversation=conversation,
        receiver_number=conversation.tenant.number,
        sender_number=conversation_number.number
    )


def get_conversation_recap_util(conversation):
    string = ''
    messages = conversation.messages.all().order_by('time_sent')
    for message in messages:
        if message.role == 'user':
            string += f"- Tenant: {message.message_content}\n\n"
        elif message.role == 'assistant':
            string += f"- Assistant: {message.message_content}\n\n"

    return string


def purchase_phone_number_util(phone_number):
    from .utils import error_handler

    try:
        webhook_url = WEBHOOK_URL + "play_the_middle_man/"
        client = Client(twilio_sid, twilio_auth_token)
        purchased_number = client.incoming_phone_numbers.create(phone_number=phone_number)
        purchased_number.update(sms_url=webhook_url)
    except TwilioRestException as e:
        print(f"Failed to purchase phone number. Error: {e}")
        error_handler(e)

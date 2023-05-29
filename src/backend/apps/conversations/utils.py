import logging

from django.db.models import Q
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import time

import openai

from conversations.models import Vendor, Conversation, Tenant, Message, PhoneNumber
from conversations.serializers import MessageSerializer
from settings.base import OPEN_API_KEY, TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, WEBHOOK_URL

openai.api_key = OPEN_API_KEY
twilio_auth_token = TWILIO_AUTH_TOKEN
twilio_sid = TWILIO_ACCOUNT_SID
logger = logging.getLogger(__name__)


def play_the_middle_man_util(request):
    # Middle man between the tenant and the vendor
    # by forwarding messages from the tenant to the vendor and vice versa

    to_number = request.POST.get('To', None)
    from_number = request.POST.get('From', None)
    body = request.POST.get('Body', None)

    conversation = PhoneNumber.objects.filter(number=to_number).first().most_recent_conversation

    is_from_tenant = conversation.tenant.number == from_number
    is_from_vendor = conversation.vendor.number == from_number

    if is_from_tenant:
        logger.info(f'- Forwarding message from tenant to vendor. Conversation: {conversation.id}')
        print(f'- Forwarding message from tenant to vendor. Conversation: {conversation.id}')
        Message.objects.create(
            message_content=body,
            sender_number=conversation.tenant.number,
            receiver_number=conversation.vendor.number,
            role="user",
            conversation=conversation
        )
        send_message(conversation.vendor.number, to_number, body)
    elif is_from_vendor:
        logger.info(f'- Forwarding message from vendor to tenant. Conversation: {conversation.id}')
        print(f'- Forwarding message from vendor to tenant. Conversation: {conversation.id}')
        Message.objects.create(
            message_content=body,
            sender_number=conversation.vendor.number,
            receiver_number=conversation.tenant.number,
            role="user",
            conversation=conversation
        )
        send_message(conversation.tenant.number, to_number, body)
    # Nothing should be returned because we're just forwarding the message
    return None


def init_conversation_util(request):
    print('- Message received!')

    # Handles the initial conversation with the tenant and sends them to a message with the vendor
    from_number = request.POST.get('From', None)
    to_number = request.POST.get('To', None)
    body = request.POST.get('Body', None)
    # reply = MessagingResponse()
    vendors = Vendor.objects.all()
    tenant, _ = Tenant.objects.get_or_create(number=from_number)
    conversation, _ = Conversation.objects.get_or_create(tenant=tenant, vendor=None)
    if conversation.messages.count() == 0:
        vocations = Vendor.objects.filter(active=True).values_list('vocation', flat=True)
        vocations_set = set(vocations)

        content = "You are a helpful assistant for Home Simple property management " \
                  "that communicates via text messages with tenants to handle and schedule their maintenance requests. " \
                  "Your primary goal is to collect the tenant's full name, address, and a detailed description of the problem they are experiencing. " \
                  "Once you have gathered this information, you need to suggest the type of profession they might need for their situation (without explicitly naming the profession in your response)." \
                  f"The profession types available include a specialist for {vocations_set}."

        Message.objects.create(
            message_content=content,
            role="system",
            conversation=conversation,
            sender_number="assistant msg",
            receiver_number="assistant msg",
        )

    Message.objects.create(
        message_content=body,
        role="user",
        conversation=conversation,
        sender_number=from_number,
        receiver_number=to_number,
    )

    conversation_json = get_conversation_messages(conversation)

    completion_from_gpt = create_chat_completion(conversation_json)

    vendor_found = get_vendor_from_conversation(conversation)
    # TODO Maybe ask tenant if the vendor sounds correct? Ask alex what to do here
    if vendor_found:
        # Hardcoded success message right before we connect the vendor and tenant
        vendor_found_response = f"Thanks! That looks good, I think our {vendor_found.vocation} is what you're looking for. " \
                                f"You should recieve a message from them soon. If this doesn't sound right, or you have any questions, " \
                                "don't hesitate to reach out to us at +1 (925) 998-1664."
        Message.objects.create(
            message_content=vendor_found_response,
            role="assistant",
            conversation=conversation,
            sender_number=to_number,
            receiver_number=from_number
        )
        start_vendor_tenant_conversation(conversation, tenant, vendor_found)
        return vendor_found_response
    else:
        Message.objects.create(
            message_content=completion_from_gpt,
            role="assistant",
            conversation=conversation,
            sender_number=to_number,
            receiver_number=from_number
        )
        return completion_from_gpt


def get_conversation_messages(conversation):
    messages = conversation.messages.all()
    serializer = MessageSerializer(messages, many=True)

    # Customize the data to match your needs
    data = []
    for item in serializer.data:
        data.append({
            'role': item['role'],
            'content': item['message_content'],
        })
    return data


def start_vendor_tenant_conversation(conversation, tenant, vendor):
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
        purchase_phone_number(number.phone_number)
        conversation_number = PhoneNumber.objects.create(number=number.phone_number,
                                                         most_recent_conversation=conversation)
    else:
        conversation_number = available_numbers.first()
        print("Using existing number:", conversation_number.number)
        conversation_number.most_recent_conversation = conversation
        conversation_number.save()

    conversation.vendor = vendor
    conversation.save()

    conversation_recap = get_conversation_recap(conversation)  # do this before we send the initial vendor message

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


def purchase_phone_number(phone_number):
    try:
        webhook_url = WEBHOOK_URL + "play_the_middle_man/"
        client = Client(twilio_sid, twilio_auth_token)
        purchased_number = client.incoming_phone_numbers.create(phone_number=phone_number)
        purchased_number.update(sms_url=webhook_url)
    except TwilioRestException as e:
        print(f"Failed to purchase phone number. Error: {e}")
        error_handler(e)


def get_vendor_from_conversation(conversation):
    # Manual (dumb) approach
    # best_vendor = None
    # vendors = Vendor.objects.all()
    #
    # for vendor in vendors:
    #     if any(keyword in response_text.lower() for keyword in vendor.keywords):
    #         best_vendor = vendor
    #         return vendor

    # GPT approach (less dumb but slower)
    vocations = ', '.join(list(Vendor.objects.filter(active=True).values_list('vocation', flat=True)))
    user_messages = ', '.join(list(conversation.messages.filter(role="user").values_list('message_content', flat=True)))

    prompt = "Respond with one word. " \
             f"Responding with only one of these terms ({vocations}), what is " \
             f"the most applicable profession for this issue that a tenant is having with their residence: " \
             f"{user_messages}"
    response = create_chat_completion([{'content': prompt, 'role': 'system'}])

    if response.lower().replace('.', '') in vocations:
        for vocation in vocations.split(', '):
            if vocation.lower() in response.lower():
                return Vendor.objects.get(vocation=vocation)
    else:
        # TODO if the vendor isn't found/correct. Probably ask for more info to user
        # TODO test this
        return None


def create_chat_completion(conversation, retry_counter=10):
    # TODO extract this so the returned value from up top waits on the retries
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.RateLimitError:
        if retry_counter > 0:
            print(f'- Rate limit. Making another request in 5s. Retries left: {retry_counter}')
            logger.error(f'- Rate limit. Making another request in 5s. Retries left: {retry_counter}')
            time.sleep(5)
            return create_chat_completion(conversation, retry_counter - 1)
        else:
            raise "Max retries exceeded."

    except Exception as e:
        error_handler(e)
        # Maybe test alex here as well/instead?
        return "Sorry, we're having some issues over here. Can you reach out directly to " \
               "your property manager, Alex at +1 (925) 998-1664.",


def send_message(to_number, from_number, message):
    try:
        # to_number HAS TO BE A TWILIO NUMBER
        client = Client(twilio_sid, twilio_auth_token)
        client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
    except TwilioRestException as e:
        error_handler(e)


def get_conversation_recap(conversation):
    string = ''
    messages = conversation.messages.all().order_by('time_sent')
    for message in messages:
        if message.role == 'user':
            string += f"- Tenant: {message.message_content}\n\n"
        elif message.role == 'assistant':
            string += f"- Assistant: {message.message_content}\n\n"

    return string


def error_handler(e):
    print("Error:", e)
    logger.error('Error: %s', e)  # This is the correct usage
    # TODO set conversation to error state, inactive, and send message to alex?
    return "Sorry, we're having some issues over here. Can you reach out directly to " \
           "your property manager, Alex at +1 (925) 998-1664."

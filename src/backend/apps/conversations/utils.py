import logging
from sys import argv

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
import time

import openai

from conversations.models import Vendor, Conversation, Tenant, Message, PhoneNumber
from conversations.serializers import MessageSerializer
from settings.base import OPEN_API_KEY, TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, WEBHOOK_URL
from .tasks import start_vendor_tenant_conversation

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
    tenant, _ = Tenant.objects.get_or_create(number=from_number)

    # TODO filter this by time as well. Should be a new convo after a few days maybe?
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
    # TODO only do vendor check if we have more than 1 user message in the conversation
    vendor_found = get_vendor_from_conversation(conversation)
    last_assistant_message = Message.objects.filter(conversation=conversation, role="assistant").last()

    confirmation_message_conditions = [
        'If that sounds like the correct vendor for your situation, reply YES, otherwise reply NO.',
        "I'm sorry! I'm a little confused. Please reply YES or NO."
    ]
    # Check if the last message from assistant was a vendor suggestion or a confusion clarification
    if last_assistant_message and confirmation_message_conditions[0] in last_assistant_message.message_content:

        # Last step -- detect vendor confirmation
        if 'yes' in body.lower() and 'no' not in body.lower():
            # Vendor is confirmed
            response = "Thanks for confirming! I'll connect you with the vendor now. You should be receiving a text " \
                       "shortly."

            if 'pytest' in argv[0]:
                # Call without delay during pytests
                start_vendor_tenant_conversation(conversation.id, vendor_found.id)
            else:
                start_vendor_tenant_conversation.delay(conversation.id, vendor_found.id)

        elif 'no' in body.lower() and 'yes' not in body.lower():
            # Vendor is denied
            response = "Oh sorry about that! You can reach out to your property manager at +1 (925) 998-1664"  # don't include period here (twilio hates it)

        else:
            # Unexpected response
            response = "I'm sorry! I'm a little confused. Please reply YES or NO."

        Message.objects.create(
            message_content=response,
            role="assistant",
            conversation=conversation,
            sender_number=to_number,
            receiver_number=from_number
        )
        return response

    elif vendor_found and Message.objects.filter(conversation=conversation, role="user").count() > 1:
        # Second to last step -- detect vendor confirmation

        # Hardcoded success message right before we connect the vendor and tenant
        vendor_found_response = f"Thanks! Sounds good, I think our {vendor_found.vocation} is best suited for your situation. " \
                                f"If that sounds like the correct vendor for your situation, reply YES, otherwise reply NO."
        Message.objects.create(
            message_content=vendor_found_response,
            role="assistant",
            conversation=conversation,
            sender_number=to_number,
            receiver_number=from_number
        )

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

    prompt = (
        "Your task is to identify the most suitable professional required for a given situation "
        "in a residential setting. You must respond with only a single word chosen from the following list of professions: {vocations}.\n\n"
        "Consider this scenario:\n"
        "{user_messages}\n\n"
        "Based on the details provided by the tenant, determine the most applicable profession required to address this issue.\n\n"
        "If the issue presented is too vague or lacks sufficient detail (such as 'I have a maintenance request' with no further explanation), "
        "you should ask for more specific information about the issue. "
        "In such cases, your response should be 'more information needed'. Remember, your response should still be limited to a single word or phrase."
    ).format(vocations=vocations, user_messages=user_messages)

    response = create_chat_completion([{'content': prompt, 'role': 'system'}])

    if response.lower().replace('.', '') in vocations:
        for vocation in vocations.split(', '):
            if vocation.lower() in response.lower():
                return Vendor.objects.get(vocation=vocation)
    else:
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
               "your property manager at +1 (925) 998-1664" # don't include period here (twilio hates it)


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


def error_handler(e):
    print("Error:", e)
    logger.error('Error: %s', e)  # This is the correct usage
    # TODO set conversation to error state, inactive, and send message to alex?
    return "Sorry, we're having some issues over here. Can you reach out directly to " \
           "your property manager at +1 (925) 998-1664" # don't include period here (twilio hates it)

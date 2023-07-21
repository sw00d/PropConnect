import logging
from sys import argv
import requests

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
import time

import openai

from companies.models import Company
from conversations.models import Vendor, Conversation, Tenant, Message, PhoneNumber, MediaMessageContent
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

    if not conversation.is_active:
        return f"This conversation is no longer active. Please text {conversation.assistant_phone_number} to start a new conversation."

    # Get media url if available
    # media_url = request.POST.get('MediaUrl0', None)  # Get the URL of the first media item, if it exists

    # you can handle more media items by looping through 'MediaUrl' parameters
    media_urls = []
    i = 0
    while request.POST.get(f'MediaUrl{i}', None):
        media_urls.append(request.POST.get(f'MediaUrl{i}'))
        i += 1

    is_from_tenant = conversation.tenant.number == from_number
    is_from_vendor = conversation.vendor.number == from_number

    if is_from_tenant:
        logger.info(f'- Forwarding message from tenant to vendor. Conversation: {conversation.id}')
        create_message_and_content(
            sender_number=conversation.tenant.number,
            receiver_number=conversation.vendor.number,
            role="user",
            conversation=conversation,
            body=body,
            media_urls=media_urls
        )
        send_message(conversation.vendor.number, to_number, body, media_urls)
    elif is_from_vendor:
        logger.info(f'- Forwarding message from vendor to tenant. Conversation: {conversation.id}')
        create_message_and_content(
            sender_number=conversation.vendor.number,
            receiver_number=conversation.tenant.number,
            role="user",
            conversation=conversation,
            body=body,
            media_urls=media_urls
        )
        send_message(conversation.tenant.number, to_number, body, media_urls)

    # Nothing should be returned because we're just forwarding the message
    return None


def create_message_and_content(sender_number, receiver_number, role, conversation, body, media_urls):
    # Create message
    message = Message.objects.create(
        message_content=body,
        sender_number=sender_number,
        receiver_number=receiver_number,
        role=role,
        conversation=conversation
    )

    # Create media message content
    for media_url in media_urls:
        if len(media_urls) < 2:
            media_type = get_media_type(media_url)
        else:
            media_type = 'other'

        MediaMessageContent.objects.create(
            media_url=media_url,
            media_type=media_type,
            message=message
        )

    return message


def handle_assistant_conversation(request):
    logger.info(
        "Message Received! \n"
        f"from number: , {request.POST.get('From', None)} \n"
        f"to number: , {request.POST.get('To', None)} \n"
        f"body: , {request.POST.get('Body', None)} \n"
    )

    # Handles the initial conversation between the tenant and the bot
    from_number = request.POST.get('From', None)
    to_number = request.POST.get('To', None)
    body = request.POST.get('Body', None)
    company = Company.objects.filter(assistant_phone_number=to_number).first()
    tenant, _ = Tenant.objects.get_or_create(number=from_number)
    tenant.company = company

    tenant.save()

    # TODO filter this by time as well. Should be a new convo after a few days maybe?
    conversation, _ = Conversation.objects.get_or_create(tenant=tenant, vendor=None)
    conversation.company = company

    conversation.save()

    logger.info(company)

    if conversation.vendor_detection_attempts > 2:
        return "Sorry, it looks like your issue is out of the scope of what this bot handles. Please contact your property manager directly."

    if company.current_subscription is None:
        return f"This assistant is not active. Please contact your property manager directly."

    if conversation.messages.count() == 0:
        vocations = Vendor.objects.filter(active=True, company=company).values_list('vocation', flat=True)
        vocations_set = set(vocations)

        content = f"You are a helpful assistant for a property management company, {conversation.company.name}," \
                  "that communicates via text messages with tenants to handle their maintenance issues. " \
                  "Your primary goal is to collect the tenant's full name, address, and a detailed description of the problem they are experiencing. " \
                  "Once you have gathered this information, you need to suggest the type of profession they might need for their situation (without explicitly naming the profession in your response)." \
                  f"The profession types available include {vocations_set}."
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

    conversation_json = get_message_history_for_gpt(conversation)

    completion_from_gpt = create_chat_completion(conversation_json)
    # TODO Only do vendor check if proposed vendor isn't populated?
    vendor_found = get_vendor_from_conversation(conversation)
    last_assistant_message = Message.objects.filter(conversation=conversation, role="assistant").last()

    confirmation_message_conditions = [
        'If that sounds like the correct vendor for your situation, reply YES, otherwise reply NO.',
        "I'm sorry! I'm a little confused. Please reply YES or NO."
    ]

    # Check if the last message from assistant was a vendor suggestion or a confusion clarification
    if last_assistant_message and confirmation_message_conditions[0] in last_assistant_message.message_content:

        yes_synonyms = ['yes', 'yep', 'yeah', 'yup', 'sure', 'absolutely', 'definitely', 'certainly', 'yea',
                        'affirmative', 'uh-huh', 'indeed', 'of course', 'true']
        no_synonyms = ['no', 'nope', 'nah', 'negative', 'not at all', 'nay', 'absolutely not', 'by no means',
                       'certainly not', 'definitely not']

        # Last step -- detect vendor confirmation
        if any(word in body.lower() for word in yes_synonyms) and not any(word in body.lower() for word in no_synonyms):
            # Vendor is confirmed
            response = "Thanks for confirming! I'll connect you with the vendor now. You should be receiving a text " \
                       "shortly."

            if 'pytest' in argv[0]:
                # Call without delay during pytests
                start_vendor_tenant_conversation(conversation.id, conversation.proposed_vendor.id)
            else:
                logger.info(f'Starting vendor tenant conversation. Conversation: {conversation.id}')
                start_vendor_tenant_conversation.delay(conversation.id, conversation.proposed_vendor.id)

        elif any(word in body.lower() for word in no_synonyms) and not any(
            word in body.lower() for word in yes_synonyms):
            logger.info(f'Vendor was denied by user. Conversation: {conversation.id}')

            # Vendor is denied
            response = "Oh sorry about that! Either tell me more specifics about your situation, or you can reach out " \
                       "to your property manager."  # don't include period here (twilio hates it)

            conversation.proposed_vendor = None
            conversation.save()

        else:
            # Unexpected response
            response = completion_from_gpt

        Message.objects.create(
            message_content=response,
            role="assistant",
            conversation=conversation,
            sender_number=to_number,
            receiver_number=from_number
        )
        send_message(from_number, to_number, response)
        return None

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
        conversation.proposed_vendor = vendor_found
        conversation.save()

        return vendor_found_response
    else:
        Message.objects.create(
            message_content=completion_from_gpt,
            role="assistant",
            conversation=conversation,
            sender_number=to_number,
            receiver_number=from_number
        )
        send_message(from_number, to_number, completion_from_gpt)
        return None


def get_message_history_for_gpt(conversation):
    messages = conversation.messages.all()
    serializer = MessageSerializer(messages, many=True)

    data = []
    for item in serializer.data:
        data.append({
            'role': item['role'],
            'content': item['message_content'],
        })
    return data


def get_vendor_from_conversation(conversation):
    # GPT approach (less dumb than keyword but still not perfect)
    vocations = "`, `".join(list(Vendor.objects.filter(active=True, company=conversation.company, company__isnull=False).values_list('vocation', flat=True)))
    user_messages = '. '.join(list(conversation.messages.filter(role="user").values_list('message_content', flat=True)))

    prompt = (
        "Pretend you are only allowed to answer with one of the following: {vocations}, 'need more information', and 'no applicable vendor'. \n\n"
        "If you don't have enough information, say 'need more information'. \n\n"
        "If the type of vendor doesn't exist in the list above say, say 'need more no applicable vendor'. \n\n"
        "The only information you have is: '{user_messages}'\n\n"
    ).format(vocations=vocations, user_messages=user_messages)

    response = create_chat_completion([{'content': prompt, 'role': 'system'}])

    if response.lower().replace('.', '') in vocations.lower():
        logger.info(f'Vendor exists within response. GPT res: {response}. Convo: {conversation}.')
        for vocation in vocations.split(', '):
            formatted_vocation = vocation.replace('`', '').lower()
            if formatted_vocation in response.lower():
                vendor = Vendor.objects.get(vocation=formatted_vocation, company=conversation.company)
                logger.info(f'Vendor found: {vendor}.')
                return vendor
    else:
        conversation.vendor_detection_attempts = conversation.vendor_detection_attempts + 1
        conversation.save()
        logger.info(f'No Vendor found. GPT res: {response}. \n\n Convo: {conversation}. \n\n Attempts: {conversation.vendor_detection_attempts}')
        return None


def create_chat_completion(conversation, retry_counter=10):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.RateLimitError:
        if retry_counter > 0:
            logger.error(f'- Rate limit. Making another request in 5s. Retries left: {retry_counter}')
            time.sleep(10)
            return create_chat_completion(conversation, retry_counter - 1)
        else:
            raise "Max retries exceeded."

    except Exception as e:
        error_handler(e)
        # Maybe test alex here as well/instead?
        return "Sorry, we're having some issues over here. Please reach out directly to " \
               "your property manager."  # don't include period here (twilio hates it)


def send_message(to_number, from_number, message, media_urls=None):
    try:
        # from_number HAS TO BE A TWILIO NUMBER
        client = Client(twilio_sid, twilio_auth_token)

        # Split message into chunks of 1600 characters each
        message_chunks = [message[i:i + 1600] for i in range(0, len(message), 1600)]

        for message_chunk in message_chunks:
            message_arguments = {
                'from_': from_number,
                'to': to_number,
                'body': message_chunk
            }

            client.messages.create(**message_arguments)

        if media_urls:
            logger.info('Sending media')
            message_arguments = {
                'from_': from_number,
                'to': to_number,
            }

            # Twilio expects a list of media URLs
            if isinstance(media_urls, list):
                message_arguments['media_url'] = media_urls
            else:
                message_arguments['media_url'] = [media_urls]
            client.messages.create(**message_arguments)

    except TwilioRestException as e:
        print(e)
        logger.error(e)
        error_handler(e)


def error_handler(e):
    logger.error('Error: %s', e)  # This is the correct usage
    # TODO set conversation to error state, inactive, and send message to prop manager?
    return "Sorry, we're having some issues over here. Please reach out directly to " \
           "your property manager."  # if ending with phone number here, don't include period (twilio hates it)


def get_media_type(url):
    # Fetch the headers of the URL without downloading the whole file
    response = requests.head(url)
    content_type = response.headers['Content-Type']

    # Determine media type based on MIME type
    if content_type.startswith('image/'):
        return 'image'
    elif content_type.startswith('video/'):
        return 'video'
    else:
        return 'other'

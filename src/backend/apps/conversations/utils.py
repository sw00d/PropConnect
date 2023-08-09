import json
import logging
from sys import argv
import requests
import threading
import queue
import time
import openai
from utils import email

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from companies.models import Company
from conversations.models import Vendor, Conversation, Tenant, Message, PhoneNumber, MediaMessageContent
from conversations.serializers import MessageSerializer
from settings.base import OPEN_API_KEY, TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, WEBHOOK_URL, TWILIO_TEST_ACCOUNT_SID, \
    TWILIO_TEST_AUTH_TOKEN

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

    if not conversation:
        return "Sorry, this conversation is no longer active. Please contact your property manager directly."

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
        message = create_message_and_content(
            sender_number=conversation.tenant.number,
            receiver_number=conversation.vendor.number,
            role="user",
            conversation=conversation,
            body=body,
            media_urls=media_urls
        )
        send_message(conversation.vendor.number, to_number, f"[TENANT]: {body}", media_urls, message_object=message)
    elif is_from_vendor:
        logger.info(f'- Forwarding message from vendor to tenant. Conversation: {conversation.id}')
        message = create_message_and_content(
            sender_number=conversation.vendor.number,
            receiver_number=conversation.tenant.number,
            role="user",
            conversation=conversation,
            body=body,
            media_urls=media_urls
        )
        send_message(conversation.tenant.number, to_number, f"[VENDOR]: {body}", media_urls, message_object=message)

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

    conversation_with_point_of_contact = Conversation.objects.filter(tenant=tenant, vendor=None, point_of_contact_has_interjected=True)

    if conversation_with_point_of_contact.exists():
        # TODO Test this
        # This is for when a prop manager has interjected and is talking to the tenant via the web app.
        # We'll want to skip all AI in this case
        # TODO Should be a web socket eventually
        Message.objects.create(
            message_content=body,
            role="user",
            conversation=conversation_with_point_of_contact.first(),
            sender_number=from_number,
            receiver_number=to_number,
        )
        return None

    # TODO filter this by time as well. Should be a new convo after a few days maybe?
    conversation, _ = Conversation.objects.get_or_create(tenant=tenant, vendor=None, waiting_on_property_manager=False)
    conversation.company = company
    conversation.save()

    logger.info(company)

    if company is None or company.current_subscription is None:
        return f"This assistant is not active. Please contact your property manager directly."

    if conversation.messages.count() == 0:
        content = f"You are a helpful assistant for a property management company, {conversation.company.name}," \
                  "that communicates via text messages with tenants to handle their maintenance issues. " \
                  "Your primary goal is to collect the tenant's full name, address, and a detailed description of the problem they are experiencing. " \
                  "Once they have provided their name and address, you can keep asking for more information over and over again. Once the user responds" \
                  "with DONE or the conversation exceeds 10 messages (but please don't tell them this)," \
                  " the property manager will be informed and the tenant will be put in contact with the vendor via" \
                  "a direct text message conversation that we set up just for their conversation. Respond to the user in responses less than 160 characters."

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

    if not tenant.name or not tenant.address:
        create_chat_completion_with_functions(conversation)

    response_to_send = create_chat_completion(conversation_json)

    done_synonyms = ['done', 'done.', 'done!']
    if body.strip().lower() in done_synonyms or conversation.messages.count() > 10:
        conversation.waiting_on_property_manager = True
        conversation.save()
        response_to_send = "Thanks for reaching out! You'll be receiving a text from our staff shortly!"
        property_manager = conversation.company.point_of_contact
        email.new_maintenance_request(property_manager.email, conversation)

    elif conversation.messages.count() > 3:
        response_to_send += "\n\n\n Reply DONE if you feel you have provided enough information."

    message = Message.objects.create(
        message_content=response_to_send,
        role="assistant",
        conversation=conversation,
        sender_number=to_number,
        receiver_number=from_number
    )
    send_message(from_number, to_number, response_to_send, message_object=message)
    return None


def get_message_history_for_gpt(conversation):
    messages = conversation.messages.all()
    serializer = MessageSerializer(messages, many=True)
    # TODO Factor in admin_to_tenant and admin roles here for messages
    data = []
    for item in serializer.data:
        content = item['message_content'].replace('\nReply DONE if you feel you have provided enough information.', '')
        print(content)
        data.append({
            'role': item['role'],
            'content': content,
        })
    return data


def create_chat_completion(conversation, retry_counter=10):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )
        print("GPT Response: ",  response['choices'][0]['message']['content'].strip())
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


def create_chat_completion_with_functions(conversation, retry_counter=10):
    messages = get_message_history_for_gpt(conversation)
    # For getting info about tenant
    functions = [
        {
            "name": "assign_tenant_name_and_address",
            "description": "Extract a name OR an address from the conversation and assign it to the tenant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of user",
                    },
                    "address": {
                        "type": "string",
                        "description": "The address of user",
                    },
                },
            },
        },
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            functions=functions
        )

        response_message = response["choices"][0]["message"]
        if response_message.get("function_call"):
            available_functions = {
                "assign_tenant_name_and_address": assign_tenant_name_and_address,
            }

            function_name = response_message["function_call"]["name"]
            function_to_call = available_functions[function_name]
            logger.info(f'GPT calling function: {function_name}')
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_to_call(
                tenant=conversation.tenant,
                name=function_args.get('name'),
                address=function_args.get('address'),
            )
        return conversation.tenant

    except KeyError as e:
        if retry_counter > 0:
            logger.error(f'- Rate limit. Making another request in 5s. Retries left: {retry_counter}')
            time.sleep(10)
            return create_chat_completion(conversation, retry_counter - 1)
        else:
            raise "Max retries exceeded."

    except json.JSONDecodeError:
        if retry_counter > 0:
            logger.error(f'- Rate limit. Making another request in 5s. Retries left: {retry_counter}')
            time.sleep(10)
            return create_chat_completion(conversation, retry_counter - 1)
        else:
            raise "Max retries exceeded."

    except openai.error.RateLimitError:
        if retry_counter > 0:
            logger.error(f'- Rate limit. Making another request in 5s. Retries left: {retry_counter}')
            time.sleep(10)
            return create_chat_completion(conversation, retry_counter - 1)
        else:
            raise "Max retries exceeded."

    except Exception as e:
        print('error', e)
        error_handler(e)
        # Maybe test alex here as well/instead?
        return "Sorry, we're having some issues over here. Please reach out directly to " \
               "your property manager."  # don't include period here (twilio hates it)


def assign_tenant_name_and_address(tenant, name, address):
    if name:
        tenant.name = name
    if address:
        tenant.address = address

    tenant.save()


def send_message(to_number, from_number, message, media_urls=None, message_object=None):
    # from_number HAS TO BE A TWILIO NUMBER
    if 'pytest' in argv[0]:
        print('pytest detected. Using test credentials.')
        client = Client(TWILIO_TEST_ACCOUNT_SID, TWILIO_TEST_AUTH_TOKEN)
        from_number = "+15005550006"  # Twilio test number -- has to be this to work in tests unless we mock
    else:
        client = Client(twilio_sid, twilio_auth_token)

    # Split message into chunks of 1600 characters each
    message_chunks = [message[i:i + 1600] for i in range(0, len(message), 1600)]
    for message_chunk in message_chunks:
        def work_message():
            logger.info(
                f'=========================== Sending message to {to_number} from {from_number}: {message_chunk}')
            try:
                message_arguments = {
                    'from_': from_number,
                    'to': to_number,
                    'body': message_chunk
                }

                client.messages.create(**message_arguments)

            except TwilioRestException as e:
                print(e)
                if message_object:
                    print("Setting error on send to true for: ", message_object)
                    message_object.error_on_send = True
                    message_object.save()

                logger.error(e)
                error_handler(e)

        # Add the work to the queue
        q.put(work_message)

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

        def work_media():
            try:
                client.messages.create(**message_arguments)
            except TwilioRestException as e:
                print(e)
                logger.error(e)
                error_handler(e)

        # Add the work to the queue
        q.put(work_media)


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


# ===============================================================
# Below is queue for sending messages, since we can only send one text message per one second per twilio campaign/service
# ===============================================================
# Create a queue
q = queue.Queue()


def worker():
    while True:
        # Get an item from the queue
        item = q.get()

        # "Process" the item (in this case, just print it)
        item()

        # Sleep for 1.5 seconds
        time.sleep(1.5)

        # Mark the item as done
        q.task_done()


# Create a worker thread
t = threading.Thread(target=worker)

# Set the thread as daemon so it will terminate when the main program terminates

t.setDaemon(True)  # TODO: this is deprecated
t.start()

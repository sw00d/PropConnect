from datetime import timedelta
from django.utils.timezone import now

from django.http import HttpRequest
from unittest.mock import patch

from openai import OpenAIError

from commands.management.commands.generate_data import generate_vendors
from conversations.models import Conversation, Vendor, PhoneNumber, Tenant, Message
from conversations.tasks import set_old_conversations_to_not_active
from conversations.utils import init_conversation_util, play_the_middle_man_util, get_conversation_recap, \
    create_chat_completion, get_vendor_from_conversation
from tests.utils import CkcAPITestCase


class TestConversations(CkcAPITestCase):

    def setUp(self):
        # seed the db
        generate_vendors()

    def test_get_vendor_from_conversation(self):
        tenant = Tenant.objects.create(number="1")  # Add necessary parameters
        vendor = Vendor.objects.first()  # Add necessary parameters
        conversation = Conversation.objects.create(tenant=tenant, vendor=vendor)

        Message.objects.create(message_content='My toilet is broken.', role="user", conversation=conversation)
        Message.objects.create(message_content='Its leaking everywhere.', role="user", conversation=conversation)

        conversation.refresh_from_db()

        response = get_vendor_from_conversation(conversation)
        assert response == Vendor.objects.get(vocation='plumber')

    @patch('conversations.utils.send_message')
    @patch('conversations.utils.purchase_phone_number')
    @patch('conversations.utils.create_chat_completion')
    def test_simple_convo_without_purchase_number(self, mock_create_chat_completion, mock_purchase_phone_number,
                                                  mock_send_message):
        PhoneNumber.objects.create(number='+5555555555', most_recent_conversation=None)

        # This is a mock message from GPT, so we can grab the "plumber" vendor.
        # user won't receive this message
        mock_create_chat_completion.return_value = "We'll put you in touch with our plumber"

        request = HttpRequest()
        request.POST = {'Body': 'My toilet is broken. Can you get me a plumber?', 'From': '+1234567890', "To": '+0987654321'}
        response = init_conversation_util(request)

        assert type(response) == str
        assert "Thanks! That looks good, I think our" in response
        assert PhoneNumber.objects.count() == 1

        request = HttpRequest()
        request.POST = {'Body': 'My toilet is broken. Can you get me a plumber?', 'From': '+1234567890', "To": '+0987654321'}
        response = init_conversation_util(request)

        assert type(response) == str
        assert "Thanks! That looks good, I think our" in response
        assert PhoneNumber.objects.count() == 2

    @patch('conversations.utils.send_message')
    @patch('conversations.utils.purchase_phone_number')
    @patch('conversations.utils.create_chat_completion')
    def test_init_conversation_util_with_purchase_number(self, mock_create_chat_completion, mock_purchase_phone_number,
                                                         mock_send_message):
        # First message
        mock_create_chat_completion.return_value = "Sorry your toilet is broken! Please provide your address, name and detailed" \
                                                   " description of the problem and I'll put you in touch with a vendor to come take a look at it."

        request = HttpRequest()
        request.POST = {'Body': 'My toilet is broken', 'From': '+1234567890', "To": '+0987654321'}
        response_from_gpt = init_conversation_util(request)

        assert type(response_from_gpt) == str
        assert response_from_gpt == "Sorry your toilet is broken! Please provide your address, name and detailed" \
                                    " description of the problem and I'll put you in touch with a vendor to come take a look at it."
        assert Conversation.objects.count() == 1
        assert Conversation.objects.first().messages.count() == 3

        # Second/follow up message(s)
        request.POST = {'Body': "Sam Wood, 4861 conrad ave, it isn't flushing and I assume it's just clogged.",
                        'From': '+1234567890', "To": '+0987654321'}

        # This is a mock message from GPT, so we can grab the "plumber" vendor.
        # user won't receive this message
        mock_create_chat_completion.return_value = "We'll put you in touch with our plumber"

        second_response = init_conversation_util(request)
        assert type(second_response) == str
        assert "Thanks! That looks good, I think our" in second_response

        # New phone number should have been purchased from twilio and created in our db
        assert PhoneNumber.objects.count() == 1
        assert PhoneNumber.objects.first().most_recent_conversation == Conversation.objects.first()
        assert Conversation.objects.first().vendor.name == 'Plumber Sam'
        assert Conversation.objects.first().messages.count() == 8

        #  Make sure a conversation was started between the two parties
        assert "You can reply directly to this number to communicate with the them" in Conversation.objects.first().messages.last().message_content
        assert Conversation.objects.first().messages.last().receiver_number == Conversation.objects.first().tenant.number

        # Test middle-man webhook/sms forwarding between vendor and tenant
        request = HttpRequest()
        request.POST = {'Body': 'Test message from tenant', 'From': Conversation.objects.first().tenant.number,
                        'To': PhoneNumber.objects.first().number}  # from tenant
        response = play_the_middle_man_util(request)
        assert Conversation.objects.first().messages.last().message_content == 'Test message from tenant'
        assert Conversation.objects.first().messages.last().sender_number == Conversation.objects.first().tenant.number

        request = HttpRequest()
        request.POST = {'Body': 'Test message from vendor', 'From': Conversation.objects.first().vendor.number,
                        'To': PhoneNumber.objects.first().number}  # from vendor
        response = play_the_middle_man_util(request)
        assert Conversation.objects.first().messages.last().message_content == 'Test message from vendor'
        assert Conversation.objects.first().messages.last().sender_number == Conversation.objects.first().vendor.number

        assert response is None  # Nothing should be returned because we're just forwarding the message

    def test_set_old_conversations_to_not_active(self):
        tenant = Tenant.objects.create(number="1")  # Add necessary parameters
        vendor = Vendor.objects.first()  # Add necessary parameters
        conversation1 = Conversation.objects.create(tenant=tenant, vendor=vendor)
        conversation2 = Conversation.objects.create(tenant=tenant, vendor=vendor)
        Message.objects.create(sender_number="123", role="user", message_content="Hello",
                               conversation=conversation1)
        Message.objects.create(sender_number="123", role="user", message_content="Hello",
                               conversation=conversation2)

        # Make one message old
        old_message = conversation1.messages.first()
        old_message.time_sent = now() - timedelta(days=4)
        old_message.save()

        set_old_conversations_to_not_active()

        conversation1.refresh_from_db()
        conversation2.refresh_from_db()

        assert conversation1.is_active is False
        assert conversation2.is_active is True

    @patch('openai.ChatCompletion.create')
    def test_create_chat_completion_with_error(self, mock_create):
        # Set up the mock object to raise an error
        mock_create.side_effect = OpenAIError('OpenAI error')

        # Call the function you are testing
        conversation = []  # add some test conversation messages here
        response = create_chat_completion(conversation)

        # Check that the error handling code was run and the expected message is returned
        assert response == ("Sorry, we're having some issues over here. Can you reach out directly to " \
                            "your property manager, Alex at 208-660-8828.",)

        # Ensure the create method was called
        mock_create.assert_called_once_with(model="gpt-3.5-turbo", messages=conversation)

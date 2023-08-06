from datetime import timedelta

import stripe
from django.core import mail
from django.utils.timezone import now

from django.http import HttpRequest
from unittest.mock import patch, Mock, MagicMock, call

from openai import OpenAIError

from commands.management.commands.generate_data import generate_vendors
from conversations.models import Conversation, Vendor, PhoneNumber, Tenant, Message
from conversations.tasks import set_old_conversations_to_not_active, start_vendor_tenant_conversation
from conversations.utils import handle_assistant_conversation, play_the_middle_man_util, \
    create_chat_completion, send_message, get_message_history_for_gpt
from tests.utils import CkcAPITestCase
from factories import CompanyFactory


class TestFullConversationFlow(CkcAPITestCase):

    @patch.object(stripe.Subscription, 'retrieve')
    def setUp(self, mock_retrieve):
        # Mock subscription
        mock_subscription = MagicMock()
        mock_retrieve.return_value = mock_subscription
        self.company = CompanyFactory.create()

        generate_vendors(self.company)

    @patch('conversations.utils.send_message')
    @patch('conversations.tasks.Client')
    @patch('conversations.tasks.purchase_phone_number_util')
    def test_start_vendor_tenant_conversation(self, mock_purchase_phone_number, mock_client, mock_send_message):
        # Arrange
        tenant = Tenant.objects.create(number="1")  # Add necessary parameters
        vendor = Vendor.objects.first()  # Add necessary parameters
        conversation = Conversation.objects.create(tenant=tenant, vendor=vendor, company=self.company)

        # Create a mock Twilio client
        mock_client_instance = mock_client.return_value
        mock_client_instance.available_phone_numbers.return_value.local.list.return_value = [
            Mock(phone_number='+0987654321')]

        # Create an available phone number for the test
        PhoneNumber.objects.create(number="+1234567890", most_recent_conversation=None, is_base_number=False)

        # Use the existing phone number
        start_vendor_tenant_conversation(conversation.id, vendor.id)

        # Assert
        conversation.refresh_from_db()  # Fetch the latest state from the database
        self.assertIsNotNone(conversation.vendor_id)
        self.assertEqual(conversation.vendor_id, vendor.id)

        phone_number = PhoneNumber.objects.get(most_recent_conversation=conversation)
        self.assertIsNotNone(phone_number)
        self.assertEqual(phone_number.number, '+1234567890')  # Verify we used the existing number

        mock_purchase_phone_number.assert_not_called()  # We should not have needed to purchase a number

        # NOW WITH PURCHASING A NUMBER
        PhoneNumber.objects.all().delete()  # Delete the existing phone number

        conversation2 = Conversation.objects.create(tenant=tenant, vendor=vendor, company=self.company)

        # Use the existing phone number
        start_vendor_tenant_conversation(conversation2.id, vendor.id)

        # Assert
        conversation2.refresh_from_db()  # Fetch the latest state from the database
        self.assertIsNotNone(conversation2.vendor_id)
        self.assertEqual(conversation2.vendor_id, vendor.id)

        phone_number = PhoneNumber.objects.get(most_recent_conversation=conversation2)
        self.assertIsNotNone(phone_number)
        self.assertNotEqual(phone_number.number, '+1234567890')  # Verify we used a new number
        assert PhoneNumber.objects.count() == 1

        mock_purchase_phone_number.assert_called()  # We should not have needed to purchase a number

    @patch.object(stripe.Subscription, 'retrieve')
    @patch('conversations.utils.send_message')
    @patch('conversations.tasks.purchase_phone_number_util')
    def test_handle_assistant_conversation_with_simple_situation(
        self,
        mock_purchase_phone_number_util,
        mock_send_message,
        mock_retrieve,
    ):

        self.company.assistant_phone_number = '+0987654321'
        test_company = self.company
        test_company.save()

        request = HttpRequest()
        request.POST = {'Body': 'Hi the storm broke my window', 'From': '+1234567890', "To": '+0987654321'}
        handle_assistant_conversation(request)

        assert Conversation.objects.count() == 1
        conversation = Conversation.objects.first()
        messages = Message.objects.all()
        assert conversation.company == test_company

        response_from_gpt = messages.last().message_content

        assert type(response_from_gpt) == str
        assert Conversation.objects.count() == 1
        assert conversation.messages.count() == 3

        # Second/follow up message(s)
        request.POST = {'Body': "Sam wood. 2323 greenleaf ave. It has a crack going across it but it's not shattered. maybe the hail got it idk",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}

        handle_assistant_conversation(request)
        second_response = conversation.messages.last().message_content
        assert 'if you feel you have provided enough information' in second_response
        assert type(second_response) == str
        assert conversation.messages.count() == 5

        # Third/follow up message(s)
        request.POST = {
            'Body': "Nope.",
            'From': '+1234567890', "To": self.company.assistant_phone_number}

        handle_assistant_conversation(request)
        third_response = conversation.messages.last().message_content
        assert 'if you feel you have provided enough information' in third_response
        assert type(third_response) == str
        assert conversation.messages.count() == 7

        # Fourth/follow up message(s)
        request.POST = {
            'Body': "Done.",
            'From': '+1234567890', "To": self.company.assistant_phone_number}

        handle_assistant_conversation(request)
        fourth_response = conversation.messages.last().message_content
        assert "You'll be receiving a text from our staff shortly!" in fourth_response
        assert type(fourth_response) == str
        assert conversation.messages.count() == 9

        assert conversation.tenant.name is not None
        assert conversation.tenant.address is not None

        assert len(mail.outbox) == 1

        #  Make sure a conversation was started between the two parties
        # assert conversation.messages.last().receiver_number == conversation.tenant.number
        #
        # # New phone number should have been purchased from twilio and created in our db
        # assert PhoneNumber.objects.count() == 1
        # assert PhoneNumber.objects.first().most_recent_conversation == conversation
        # conversation.refresh_from_db()
        #
        # assert conversation.vendor.name == 'Appliance Specialist Sam'
        # assert conversation.messages.count() == 18
        #
        # # Test middle-man webhook/sms forwarding between vendor and tenant
        # request = HttpRequest()
        # request.POST = {'Body': 'Test message from tenant', 'From': conversation.tenant.number,
        #                 'To': PhoneNumber.objects.first().number}  # from tenant
        # response = play_the_middle_man_util(request)
        # assert conversation.messages.last().message_content == 'Test message from tenant'
        # assert conversation.messages.last().sender_number == conversation.tenant.number
        #
        # request = HttpRequest()
        # request.POST = {'Body': 'Test message from vendor', 'From': conversation.vendor.number,
        #                 'To': PhoneNumber.objects.first().number}  # from vendor
        # response = play_the_middle_man_util(request)
        # assert conversation.messages.last().message_content == 'Test message from vendor'
        # assert conversation.messages.last().sender_number == Conversation.objects.first().vendor.number
        #
        # assert conversation.company == self.company
        #
        # assert response is None  # Nothing should be returned because we're just forwarding the message

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

        set_old_conversations_to_not_active(0)
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
        assert response == "Sorry, we're having some issues over here. Please reach out directly to " \
                           "your property manager."

        # Ensure the create method was called
        mock_create.assert_called_once_with(model="gpt-3.5-turbo", messages=conversation)


from datetime import timedelta
from django.utils.timezone import now

from django.http import HttpRequest
from unittest.mock import patch, Mock

from openai import OpenAIError

from commands.management.commands.generate_data import generate_vendors
from conversations.models import Conversation, Vendor, PhoneNumber, Tenant, Message
from conversations.tasks import set_old_conversations_to_not_active, start_vendor_tenant_conversation
from conversations.utils import init_conversation_util, play_the_middle_man_util, \
    create_chat_completion, get_vendor_from_conversation
from tests.utils import CkcAPITestCase


class TestFullConversationFlowx(CkcAPITestCase):

    def setUp(self):
        # seed the db
        generate_vendors()

    @patch('conversations.utils.send_message')
    @patch('conversations.tasks.Client')
    @patch('conversations.tasks.purchase_phone_number_util')
    def test_start_vendor_tenant_conversation(self, mock_purchase_phone_number, mock_client, mock_send_message):
        # Arrange
        tenant = Tenant.objects.create(number="1")  # Add necessary parameters
        vendor = Vendor.objects.first()  # Add necessary parameters
        conversation = Conversation.objects.create(tenant=tenant, vendor=vendor)

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

        conversation2 = Conversation.objects.create(tenant=tenant, vendor=vendor)

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

    @patch('conversations.utils.send_message')
    @patch('conversations.tasks.purchase_phone_number_util')
    @patch('conversations.utils.create_chat_completion')
    def test_init_conversation_util_with_purchase_number(
        self,
        mock_create_chat_completion,
        mock_purchase_phone_number_util,
        mock_send_message
    ):
        # First message
        mock_create_chat_completion.return_value = "Sorry your toilet is broken! Please provide your address, name and detailed" \
                                                   " description of the problem and I'll put you in touch with a vendor to come take a look at it."

        request = HttpRequest()
        request.POST = {'Body': 'My toilet is broken', 'From': '+1234567890', "To": '+0987654321'}
        init_conversation_util(request)
        response_from_gpt = Conversation.objects.first().messages.last().message_content

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
        mock_create_chat_completion.return_value = "Handyman."

        init_conversation_util(request)
        second_response = Conversation.objects.first().messages.last().message_content
        assert "Thanks! Sounds good, I think our handyman" in second_response

        # This will hit GPT so we can get more info from the tenant
        mock_res = "Can you please tell me more about the situation? Is the wall wet due to a leak?"
        mock_create_chat_completion.return_value = mock_res
        request.POST = {'Body': "Idk",
                        'From': '+1234567890', "To": '+0987654321'}
        init_conversation_util(request)
        third_response = Conversation.objects.first().messages.last().message_content
        assert mock_res == third_response

        # This is a mock message from GPT, so we can grab the "plumber" vendor.
        # user won't receive this message
        mock_create_chat_completion.return_value = "Plumber."

        request.POST = {'Body': "It's leaking everywhere. Seems like a plumber would be better",
                        'From': '+1234567890', "To": '+0987654321'}
        init_conversation_util(request)
        fourth_respsonse = Conversation.objects.first().messages.last().message_content
        assert "Thanks! Sounds good, I think our plumber" in fourth_respsonse

        request.POST = {'Body': "NO",
                        'From': '+1234567890', "To": '+0987654321'}
        init_conversation_util(request)
        fifth_response = Conversation.objects.first().messages.last().message_content
        assert "Oh sorry about that! Either tell me more specifics about your situation" in fifth_response

        # This is a mock message from GPT, so we can grab the "plumber" vendor.
        # user won't receive this message
        mock_create_chat_completion.return_value = "Appliance Specialist"

        request.POST = {'Body': "It's leaking everywhere. Seems like an appliance specialist would be better",
                        'From': '+1234567890', "To": '+0987654321'}
        init_conversation_util(request)
        sixth_response = Conversation.objects.first().messages.last().message_content
        assert "Thanks! Sounds good, I think our appliance" in sixth_response

        request.POST = {'Body': "YES",
                        'From': '+1234567890', "To": '+0987654321'}
        init_conversation_util(request)
        seventh_response = Conversation.objects.first().messages.last().message_content
        assert "Thanks for confirming! I'll connect you with the vendor now. You should be receiving a text shortly." == seventh_response

        #  Make sure a conversation was started between the two parties
        assert Conversation.objects.first().messages.last().receiver_number == Conversation.objects.first().tenant.number

        # New phone number should have been purchased from twilio and created in our db
        assert PhoneNumber.objects.count() == 1
        assert PhoneNumber.objects.first().most_recent_conversation == Conversation.objects.first()
        assert Conversation.objects.first().vendor.name == 'Appliance Specialist Sam'
        assert Conversation.objects.first().messages.count() == 18

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

        set_old_conversations_to_not_active(0)
        assert conversation1.is_active is False
        assert conversation2.is_active is True

    def test_get_vendor_from_conversation(self):
        tenant = Tenant.objects.create(number="1")  # Add necessary parameters
        vendor = Vendor.objects.first()  # Add necessary parameters
        conversation = Conversation.objects.create(tenant=tenant, vendor=vendor)

        Message.objects.create(message_content='My toilet is broken.', role="user", conversation=conversation)
        Message.objects.create(message_content='Its leaking everywhere.', role="user", conversation=conversation)

        conversation.refresh_from_db()

        response = get_vendor_from_conversation(conversation)
        assert response == Vendor.objects.get(vocation='plumber')

    @patch('openai.ChatCompletion.create')
    def test_create_chat_completion_with_error(self, mock_create):
        # Set up the mock object to raise an error
        mock_create.side_effect = OpenAIError('OpenAI error')

        # Call the function you are testing
        conversation = []  # add some test conversation messages here
        response = create_chat_completion(conversation)

        # Check that the error handling code was run and the expected message is returned
        assert response == "Sorry, we're having some issues over here. Can you reach out directly to " \
                           "your property manager at +1 (925) 998-1664"

        # Ensure the create method was called
        mock_create.assert_called_once_with(model="gpt-3.5-turbo", messages=conversation)
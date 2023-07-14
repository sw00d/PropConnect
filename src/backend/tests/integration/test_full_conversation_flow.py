from datetime import timedelta

import stripe
from django.utils.timezone import now

from django.http import HttpRequest
from unittest.mock import patch, Mock, MagicMock, call

from openai import OpenAIError

from commands.management.commands.generate_data import generate_vendors
from conversations.models import Conversation, Vendor, PhoneNumber, Tenant, Message
from conversations.tasks import set_old_conversations_to_not_active, start_vendor_tenant_conversation
from conversations.utils import handle_assistant_conversation, play_the_middle_man_util, \
    create_chat_completion, get_vendor_from_conversation, send_message, get_message_history_for_gpt
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
    @patch('conversations.utils.create_chat_completion')
    def test_handle_assistant_conversation_with_complex_situation(
        self,
        mock_create_chat_completion,
        mock_purchase_phone_number_util,
        mock_send_message,
        mock_retrieve,
    ):
        # -----------------------------
        # TLDR:
        # 1: This subs all gpt/twilio responses.
        # 2: It tests a complex flow in which GPT guesses wrong and has to get more info
        # 3: It also tests the  purchasing a new twilio number (subs the request of course)
        # -----------------------------

        self.company.assistant_phone_number = '+0987654321'
        test_company = self.company
        test_company.save()

        # First message
        mock_create_chat_completion.return_value = "Sorry your toilet is broken! Please provide your address, name and detailed" \
                                                   " description of the problem and I'll put you in touch with a vendor to come take a look at it."

        request = HttpRequest()
        request.POST = {'Body': 'My toilet is broken', 'From': '+1234567890', "To": '+0987654321'}
        handle_assistant_conversation(request)

        assert Conversation.objects.count() == 1
        conversation = Conversation.objects.first()
        messages = Message.objects.all()
        assert conversation.company == test_company

        response_from_gpt = messages.last().message_content

        assert type(response_from_gpt) == str
        assert response_from_gpt == "Sorry your toilet is broken! Please provide your address, name and detailed" \
                                    " description of the problem and I'll put you in touch with a vendor to come take a look at it."
        assert Conversation.objects.count() == 1
        assert conversation.messages.count() == 3

        # Second/follow up message(s)
        request.POST = {'Body': "Sam Wood, 4861 conrad ave, it isn't flushing and I assume it's just clogged.",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}

        # # This is a mock message from GPT, so we can grab the "plumber" vendor.
        # # user won't receive this message
        mock_create_chat_completion.return_value = "Plumber"

        handle_assistant_conversation(request)
        second_response = conversation.messages.last().message_content
        assert 'Thanks! Sounds good, I think our plumber is best' in second_response

        # This will hit GPT so we can get more info from the tenant
        mock_res = "Can you please tell me more about the situation? Is the wall wet due to a leak?"
        mock_create_chat_completion.return_value = mock_res
        request.POST = {'Body': "Idk",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}
        handle_assistant_conversation(request)
        third_response = conversation.messages.last().message_content
        assert mock_res == third_response

        print(third_response)
        # This is a mock message from GPT, so we can grab the "plumber" vendor.
        # user won't receive this message
        mock_create_chat_completion.return_value = "Plumber."

        request.POST = {'Body': "It's leaking everywhere. Seems like a plumber would be better",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}
        handle_assistant_conversation(request)
        fourth_respsonse = conversation.messages.last().message_content
        assert "Thanks! Sounds good, I think our plumber" in fourth_respsonse

        request.POST = {'Body': "NO",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}
        handle_assistant_conversation(request)
        fifth_response = conversation.messages.last().message_content
        assert "Oh sorry about that! Either tell me more specifics about your situation" in fifth_response

        # This is a mock message from GPT, so we can grab the "plumber" vendor.
        # user won't receive this message
        mock_create_chat_completion.return_value = "Appliance Specialist"

        request.POST = {'Body': "It's leaking everywhere. Seems like an appliance specialist would be better",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}
        handle_assistant_conversation(request)
        sixth_response = conversation.messages.last().message_content
        assert "Thanks! Sounds good, I think our appliance" in sixth_response

        request.POST = {'Body': "YES",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}
        handle_assistant_conversation(request)
        seventh_response = conversation.messages.last().message_content
        assert "Thanks for confirming! I'll connect you with the vendor now. You should be receiving a text shortly." == seventh_response

        #  Make sure a conversation was started between the two parties
        assert conversation.messages.last().receiver_number == conversation.tenant.number

        # New phone number should have been purchased from twilio and created in our db
        assert PhoneNumber.objects.count() == 1
        assert PhoneNumber.objects.first().most_recent_conversation == conversation
        conversation.refresh_from_db()

        assert conversation.vendor.name == 'Appliance Specialist Sam'
        assert conversation.messages.count() == 18

        # Test middle-man webhook/sms forwarding between vendor and tenant
        request = HttpRequest()
        request.POST = {'Body': 'Test message from tenant', 'From': conversation.tenant.number,
                        'To': PhoneNumber.objects.first().number}  # from tenant
        response = play_the_middle_man_util(request)
        assert conversation.messages.last().message_content == 'Test message from tenant'
        assert conversation.messages.last().sender_number == conversation.tenant.number

        request = HttpRequest()
        request.POST = {'Body': 'Test message from vendor', 'From': conversation.vendor.number,
                        'To': PhoneNumber.objects.first().number}  # from vendor
        response = play_the_middle_man_util(request)
        assert conversation.messages.last().message_content == 'Test message from vendor'
        assert conversation.messages.last().sender_number == Conversation.objects.first().vendor.number

        assert conversation.company == self.company

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
        company = self.company
        conversation = Conversation.objects.create(tenant=tenant, vendor=vendor)

        Message.objects.create(message_content='My toilet is broken.', role="user", conversation=conversation)
        Message.objects.create(message_content='Its leaking everywhere.', role="user", conversation=conversation)

        conversation.refresh_from_db()

        # conversation has no vendors yet so return None
        response = get_vendor_from_conversation(conversation)
        assert response is None

        conversation.company = company

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
        assert response == "Sorry, we're having some issues over here. Please reach out directly to " \
                           "your property manager."

        # Ensure the create method was called
        mock_create.assert_called_once_with(model="gpt-3.5-turbo", messages=conversation)

    @patch('conversations.utils.Client')
    def test_send_message_too_long(self, mock_client):
        # Prepare
        message = "Hello World!" * 200
        to_number = "+1234567890"
        from_number = "+0987654321"

        # Create a mock Twilio client
        client_instance = mock_client.return_value

        client_instance.messages.create = MagicMock()
        mock_client.return_value = client_instance

        # Run
        send_message(to_number, from_number, message)

        # Assert
        assert client_instance.messages.create.call_count == 2  # Check that the method was called twice

        expected_calls = [
            call(from_=from_number, to=to_number, body=message[:1600]),
            call(from_=from_number, to=to_number, body=message[1600:]),
        ]
        client_instance.messages.create.assert_has_calls(expected_calls, any_order=False)  # Check the call arguments

    @patch.object(stripe.Subscription, 'retrieve')
    @patch('conversations.utils.send_message')
    @patch('conversations.tasks.purchase_phone_number_util')
    def test_conversation_that_doesnt_match_any_vendor(
        self,
        mock_purchase_phone_number_util,
        mock_send_message,
        mock_retrieve,
    ):
        # delete all vendors
        Vendor.objects.all().delete()

        self.company.assistant_phone_number = '+0987654321'
        test_company = self.company
        Vendor.objects.create(name="Painter Sam", vocation="painter", company=self.company)
        test_company.save()

        request = HttpRequest()
        request.POST = {'Body': 'My toilet is broken', 'From': '+1234567890', "To": self.company.assistant_phone_number}
        handle_assistant_conversation(request)
        conversation = Conversation.objects.filter(company=test_company).first()

        assert Conversation.objects.count() == 1
        assert conversation.company == test_company
        assert conversation.vendor_detection_attempts == 1

        messages = Message.objects.filter(conversation=conversation)
        assert conversation.company == test_company

        response_from_gpt = messages.last().message_content

        assert type(response_from_gpt) == str
        assert Conversation.objects.count() == 1
        assert conversation.messages.count() == 3

        request.POST = {'Body': "Sam Wood, 4861 conrad ave, it isn't flushing and I assume it's just clogged.",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}
        handle_assistant_conversation(request)
        conversation.refresh_from_db()
        response = conversation.messages.last().message_content
        assert "Thanks! Sounds good" not in response  # standard response when vendor is found
        assert conversation.vendor_detection_attempts == 2

        request.POST = {'Body': "There is water everywhere and I don't know what to do.",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}
        handle_assistant_conversation(request)
        conversation.refresh_from_db()
        response = conversation.messages.last().message_content
        assert "Thanks! Sounds good" not in response
        assert conversation.vendor_detection_attempts == 3

        request.POST = {'Body': "I just feel like a plumber would be a good idea here",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}
        handle_assistant_conversation(request)
        conversation.refresh_from_db()
        response = conversation.messages.last().message_content
        assert "Thanks! Sounds good" not in response
        assert conversation.vendor_detection_attempts == 4

        request.POST = {'Body': "It seems like it's gonna ruin my bathroom floor",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}
        handle_assistant_conversation(request)
        conversation.refresh_from_db()
        response = conversation.messages.last().message_content
        assert "Thanks! Sounds good" not in response
        assert conversation.vendor_detection_attempts == 5

        request.POST = {'Body': "Should I plunge it?",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}
        handle_assistant_conversation(request)
        conversation.refresh_from_db()
        response = conversation.messages.last().message_content
        assert "Thanks! Sounds good" not in response
        assert conversation.vendor_detection_attempts == 6

        request.POST = {'Body': "Thanks for your help but i'm lost.",
                        'From': '+1234567890', "To": self.company.assistant_phone_number}
        res = handle_assistant_conversation(request)
        assert res == "Sorry, it looks like your issue is out of the scope of what this bot handles. Please contact your property manager directly."

        conversation.refresh_from_db()
        response = conversation.messages.last().message_content
        assert "Thanks! Sounds good" not in response


from unittest.mock import patch, Mock

from twilio.rest import Client

from twilio.base.exceptions import TwilioRestException

from commands.management.commands.generate_data import generate_vendors
from conversations.models import Message, Vendor, PhoneNumber
from conversations.tasks import purchase_phone_number_util, send_message_task, get_conversation_recap_util
from factories import ConversationFactory, UserFactory, CompanyFactory, MessageFactory
from settings.base import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID
from tests.utils import CkcAPITestCase
from django.urls import reverse
from rest_framework import status
from django.utils.timezone import now


class ConversationViewSetTestCase(CkcAPITestCase):
    def setUp(self):
        generate_vendors()

        self.admin_user = UserFactory(is_staff=True)
        self.company1 = CompanyFactory()
        self.company2 = CompanyFactory()
        self.normal_user1 = UserFactory(company=self.company1)
        self.normal_user2 = UserFactory(company=self.company2)

        self.conversation = ConversationFactory.create(vendor=Vendor.objects.first())
        self.conversation1 = ConversationFactory.create(vendor=Vendor.objects.first(), company=self.company1)
        self.conversation2 = ConversationFactory.create(vendor=Vendor.objects.first(), company=self.company2)

        self.detail_url = reverse('conversations-detail', kwargs={'pk': self.conversation.pk})

    def test_user_can_only_list_their_conversations(self):
        self.client.force_authenticate(self.normal_user1)
        request = reverse('conversations-detail', kwargs={'pk': self.conversation2.pk})
        response = self.client.get(request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        request = reverse('conversations-detail', kwargs={'pk': self.conversation1.pk})
        response = self.client.get(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        request = reverse('conversations-list')
        response = self.client.get(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0].get('id'), self.conversation1.pk)

        self.client.force_authenticate(self.normal_user2)
        request = reverse('conversations-detail', kwargs={'pk': self.conversation2.pk})
        response = self.client.get(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        request = reverse('conversations-detail', kwargs={'pk': self.conversation1.pk})
        response = self.client.get(request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        request = reverse('conversations-list')
        response = self.client.get(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0].get('id'), self.conversation2.pk)

        # --------------------------------------------
        # Makes sure users with no company or convos can't access any conversations
        # --------------------------------------------
        self.client.force_authenticate(UserFactory())
        request = reverse('conversations-detail', kwargs={'pk': self.conversation2.pk})
        response = self.client.get(request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        request = reverse('conversations-detail', kwargs={'pk': self.conversation1.pk})
        response = self.client.get(request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        request = reverse('conversations-list')
        response = self.client.get(request)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('conversations.utils.send_message')
    @patch('conversations.tasks.Client')
    @patch('conversations.tasks.purchase_phone_number_util')
    def test_assign_vendor(self, mock_purchase_phone_number, mock_client, mock_send_message):
        mock_client_instance = mock_client.return_value
        mock_client_instance.available_phone_numbers.return_value.local.list.return_value = [
            Mock(phone_number='+0987654321')]

        # Create an available phone number for the test
        PhoneNumber.objects.create(number="+1234567895", most_recent_conversation=None, is_base_number=False)

        data = {
            'vendor': Vendor.objects.first().pk,
            'tenant_intro_message': 'Hello, this is a test tenant message',
            'vendor_intro_message': 'Hello, this is a test vendor message',
        }
        user = UserFactory(company=self.company1)
        conversation = ConversationFactory.create(vendor=None, company=self.company1)

        url = reverse('conversations-assign-vendor', kwargs={'pk': conversation.pk})
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # Not authed users should get 401

        self.client.force_authenticate(user)
        assert conversation.vendor is None
        response = self.client.post(url, data)
        conversation.refresh_from_db()

        self.assertIsNotNone(conversation.vendor_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert conversation.vendor.id == Vendor.objects.first().pk
        assert conversation.tenant_intro_message == 'Hello, this is a test tenant message'
        assert conversation.vendor_intro_message == 'Hello, this is a test vendor message'

        phone_number = PhoneNumber.objects.get(most_recent_conversation=conversation)
        self.assertEqual(phone_number.number, '+1234567895')  # Verify we used the existing number

        mock_purchase_phone_number.assert_not_called()  # We should not have needed to purchase a number

        assert Message.objects.all().last().message_content == 'Hello, this is a test tenant message'

    def test_get_conversation_recap_util(self):
        conversation = ConversationFactory()  # Assuming a simple create works. Adjust as needed.

        MessageFactory(message_content="Hi! I need help.", role="user", conversation=conversation)
        MessageFactory(message_content="What do you need help with? Reply DONE if you feel you have provided enough information.", role="assistant", conversation=conversation)
        MessageFactory(message_content="My faucet is broken.", role="user", conversation=conversation)
        MessageFactory(message_content="How's it broken? Reply DONE if you feel you have provided enough information.", role="assistant", conversation=conversation)
        MessageFactory(message_content="It has a crack in it.", role="user", conversation=conversation)
        MessageFactory(message_content="Can I have your email and address and stuff? Reply DONE if you feel you have provided enough information.", role="assistant", conversation=conversation)
        MessageFactory(message_content="Sam wood. 2032 greenleaf ave. san diego", role="user", conversation=conversation)

        recap = get_conversation_recap_util(conversation)

        # Check that the recap contains all messages
        self.assertIn("Hi! I need help.", recap)
        self.assertIn("What do you need help with?", recap)
        self.assertIn("My faucet is broken.", recap)

        # Check that the special string is removed
        self.assertNotIn("Reply DONE if you feel you have provided enough information.", recap)

        # Check that messages are ordered by their time_sent
        self.assertTrue(recap.index("Hi! I need help.") < recap.index("What do you need help with?"))

        # Check that the recap contains the right prefixes
        self.assertIn("- Tenant: Hi! I need help.", recap)
        self.assertIn("- Assistant: What do you need help with?", recap)
        self.assertIn("- Tenant: My faucet is broken.", recap)

    def test_set_last_viewed(self):
        time = now()
        url = reverse('conversations-set-last-viewed', kwargs={'pk': self.conversation1.pk})
        response = self.client.post(url)
        self.conversation1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # Not authed users should get 401

        self.client.force_authenticate(self.normal_user1)
        response = self.client.post(url)
        self.conversation1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(self.conversation1.last_viewed, time)

    def test_purchase_toll_free_phone_number(self):
        # --------------------------------------------
        # Doing what we can here with test credentials (very limited atm)
        # --------------------------------------------
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        number = client.available_phone_numbers("US").toll_free.list(limit=3)[0]

        # we have to use +15005550006 because that's the only number we can use in test mode
        purchased_number = purchase_phone_number_util('+15005550006', api_endpoint="/init_conversation/",
                                                      type_of_number='toll_free')

        assert number.phone_number.startswith('+18')
        assert purchased_number is not None
        assert purchased_number.sms_url == 'https://propconnect.io/init_conversation/'
        # assert purchased_number.address_sid is not None # test for these eventually. Not working atm
        # assert purchased_number.emergency_address_sid is not None # test for these eventually. Not working atm

    @patch('conversations.tasks.logger')
    @patch('conversations.tasks.Client')
    def test_send_message_using_test_credentials(self, mock_client, mock_logger):
        body = 'Hello World'
        send_message_task('+12086608828', '+15005550006', body)
        mock_client().messages.create.assert_called_with(from_='+15005550006', to='+12086608828', body=body)
        mock_logger.info.assert_called_with(
            '=========================== Sending message to +12086608828 from +15005550006: Hello World')

    @patch('conversations.utils.error_handler')
    @patch('conversations.tasks.logger')
    @patch('conversations.tasks.Client')
    def test_send_message_with_error(self, mock_client, mock_logger, mock_error_handler):
        mock_client().messages.create.side_effect = TwilioRestException("Failed", "url", "method", 400)
        message_object = MessageFactory(message_content="Hello im an error")
        send_message_task('+12086608828', '+15005550006', message_object.message_content, message_object_id=message_object.id)
        message_object.refresh_from_db()
        assert message_object.error_on_send
        assert message_object.message_content == 'Hello im an error'
        mock_error_handler.assert_called_once()

    @patch('conversations.tasks.logger')
    @patch('conversations.tasks.Client')
    def test_send_message_split_into_chunks(self, mock_Client, mock_logger):
        # Mock the create method on Client's instance.
        mock_client_instance = mock_Client.return_value
        mock_client_instance.messages.create = Mock()

        long_message = 'A' * 1600 + 'B' * 1600 + 'C' * 123  # 2 chunks of 1600 characters
        send_message_task('+12086608828', '+15005550006', long_message)
        assert mock_logger.info.call_count == 3
        assert mock_client_instance.messages.create.call_count == 3

        # Validate that the messages sent are actually the correct chunks.
        first_call, first_args = mock_client_instance.messages.create.call_args_list[0]
        second_call, second_args = mock_client_instance.messages.create.call_args_list[1]
        third_call, third_args = mock_client_instance.messages.create.call_args_list[2]
        # second_call_args, _ = mock_client_instance.messages.create.call_args_list[1]

        assert first_args['body'] == 'A' * 1600
        assert second_args['body'] == 'B' * 1600
        assert third_args['body'] == 'C' * 123

    @patch('conversations.tasks.logger')
    @patch('conversations.tasks.Client')
    def test_send_media(self, mock_Client, mock_logger):
        # Mock the create method on Client's instance.
        mock_client_instance = mock_Client.return_value
        mock_client_instance.messages.create = Mock()

    def test_send_message_task_rate_limit(self):
        assert send_message_task.rate_limit == '0.66/s'

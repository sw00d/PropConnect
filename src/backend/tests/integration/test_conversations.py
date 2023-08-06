from queue import Queue
from unittest import skip
from unittest.mock import patch, MagicMock
from twilio.rest import Client

from twilio.base.exceptions import TwilioRestException

from commands.management.commands.generate_data import generate_vendors
from conversations.models import Message, Vendor, Conversation, Tenant
from conversations.tasks import purchase_phone_number_util
from conversations.utils import send_message, q
from factories import ConversationFactory, UserFactory, TwilioNumberFactory, CompanyFactory
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

    # --------------------------------------------
    # TODO Fix the tests below this. Testing the queue is proving hard. Running them individually is more reliable than running them all at once
    # --------------------------------------------
    @patch('conversations.utils.Client')
    @skip('Queue has a hard time when running test suite')
    def test_send_admin_message(self, mock_client):
        mock_messages = MagicMock()
        mock_client.return_value.messages = mock_messages

        self.client.force_authenticate(self.normal_user1)

        url = reverse('conversations-send-admin-message', kwargs={'pk': self.conversation2.pk})

        TwilioNumberFactory(most_recent_conversation=self.conversation2)
        self.conversation1.refresh_from_db()

        assert self.conversation2.twilio_number is not None
        response = self.client.post(url, data={"message_body": "test message"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        TwilioNumberFactory(most_recent_conversation=self.conversation1)
        self.conversation1.refresh_from_db()

        assert self.conversation1.twilio_number is not None
        url = reverse('conversations-send-admin-message', kwargs={'pk': self.conversation1.pk})
        response = self.client.post(url, data={"message_body": "test message"})
        self.assertEqual(q.qsize(), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        message_count = Message.objects.filter(
            conversation=self.conversation1,
            message_content="test message",
            role="admin"
        ).count()

        self.assertEqual(message_count, 1)
        q.join()

    @patch('conversations.utils.Client')
    @skip('Queue has a hard time when running test suite')
    def test_send_message_util(self, mock_client):
        mock_messages = MagicMock()
        mock_client.return_value.messages = mock_messages
        send_message('+1234567890', '+0987654321', 'Test message')
        self.assertEqual(q.qsize(), 1)
        q.join()

    @patch('conversations.utils.Client')
    @skip('Queue has a hard time when running test suite')
    def test_send_message_exception(self, mock_client):
        mock_messages = MagicMock()
        mock_messages.create.side_effect = TwilioRestException('Test error', 'Test message')
        mock_client.return_value.messages = mock_messages
        send_message('+1234567890', '+0987654321', 'Test message')
        self.assertEqual(q.qsize(), 1)
        q.join()

    @patch('conversations.utils.Client')
    @skip('Queue has a hard time when running test suite')
    def test_send_message_media_urls(self, mock_client):
        mock_messages = MagicMock()
        mock_client.return_value.messages = mock_messages
        send_message('+1234567890', '+0987654321', 'Test message', media_urls='http://example.com/test.jpg')
        self.assertEqual(q.qsize(), 2)
        q.join()

    @patch('conversations.utils.Client')
    @skip('Queue has a hard time when running test suite')
    def test_multiple_send_message_calls(self, mock_client):
        # Prepare
        message = "Hello World!"
        to_number = "+1234567890"
        from_number = "+0987654321"

        # Create a mock Twilio client
        client_instance = mock_client.return_value

        client_instance.messages.create = MagicMock()
        mock_client.return_value = client_instance

        qsizes = []
        for _ in range(4):
            send_message(to_number, from_number, message)
            qsizes.append(q.qsize())

        self.assertEqual(len(qsizes), 4)
        q.join()
        self.assertEqual(q.qsize(), 0)

    @patch('conversations.utils.Client')
    @skip('Queue has a hard time when running test suite')
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

        # Wait for the queue to empty
        self.assertEqual(q.qsize(), 2)
        q.join()
        self.assertEqual(q.qsize(), 0)


class SendMessageTest(CkcAPITestCase):
    @patch('conversations.utils.Client')
    def test_send_message_error_setting_message_field(self, mock_client):
        # Create the mock Twilio client
        mock_messages = MagicMock()
        mock_messages.create.side_effect = TwilioRestException('Test error', 'Test message')
        mock_client.return_value.messages = mock_messages

        # Create mock message object with necessary attributes
        mock_message_object = MagicMock()
        mock_message_object.id = 1
        mock_message_object.error_on_send = False

        # Create queue
        q = Queue()

        # Replace 'your_module' with the name of the actual module where `send_message` is defined
        with patch('conversations.utils.q', q):
            # Run send_message function
            send_message('+1234567890', '+0987654321', 'test message', message_object=mock_message_object)

        # Get the queued function and execute it
        work_message = q.get()
        work_message()

        # Check that the error_on_send attribute was updated
        self.assertTrue(mock_message_object.error_on_send)

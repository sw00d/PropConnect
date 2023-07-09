from unittest.mock import patch
import pytest

from commands.management.commands.generate_data import generate_vendors
from conversations.models import Message, Vendor
from factories import ConversationFactory, UserFactory, TwilioNumberFactory
from tests.utils import CkcAPITestCase
from django.urls import reverse
from rest_framework import status
from django.utils.timezone import now


class ConversationViewSetTestCase(CkcAPITestCase):
    def setUp(self):
        generate_vendors()

        self.admin_user = UserFactory(is_staff=True)

        self.conversation = ConversationFactory.create(vendor=Vendor.objects.first())
        self.detail_url = reverse('conversation-detail', kwargs={'pk': self.conversation.pk})

    def test_list_conversations(self):
        list_url = reverse('conversation-list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.admin_user)
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_set_last_viewed(self):
        self.client.force_authenticate(self.admin_user)
        time = now()
        response = self.client.post(f"{self.detail_url}set_last_viewed/")
        self.conversation.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(self.conversation.last_viewed, time)

    # @pytest.mark.skip("TODO: fix this test")
    @patch('conversations.utils.send_message')
    def test_send_admin_message(self, mock_send_message):
        admin_message_url = f"{self.detail_url}send_admin_message/"
        TwilioNumberFactory(most_recent_conversation=self.conversation)
        self.conversation.refresh_from_db()

        response = self.client.post(admin_message_url, data={"message_body": "test message"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        print("1: Should be a number: ", self.conversation.twilio_number)  # This exists
        self.conversation.refresh_from_db()
        print("2: Should be a number: ", self.conversation.twilio_number)  # This doesn't exist, but needs to exist

        self.client.force_authenticate(self.admin_user)
        response = self.client.post(admin_message_url, data={"message_body": "test message"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        message_count = Message.objects.filter(
            conversation=self.conversation,
            message_content="test message",
            role="admin"
        ).count()

        self.assertEqual(message_count, 1)

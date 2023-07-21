from unittest.mock import patch

from commands.management.commands.generate_data import generate_vendors
from conversations.models import Message, Vendor
from conversations.tasks import purchase_phone_number_util
from factories import ConversationFactory, UserFactory, TwilioNumberFactory, CompanyFactory
from settings.base import WEBHOOK_URL
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

    @patch('conversations.views.send_message')
    def test_send_admin_message(self, mock_send_message):
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        message_count = Message.objects.filter(
            conversation=self.conversation1,
            message_content="test message",
            role="admin"
        ).count()

        self.assertEqual(message_count, 1)

    # def test_purchase_toll_free_number(self):
    #     # Must use twilio test creds
    #     purchased_number = purchase_phone_number_util(
    #         '+15005550006',
    #         api_endpoint='/init_conversation',
    #         type_of_number='toll-free',
    #     )
    #
    #     self.assertEqual(purchased_number.phone_number, '+15005550006')
    #     assert purchased_number.capabilities['sms'] is True
    #     assert purchased_number.capabilities['voice'] is False
    #     assert purchased_number.sms_url == f"{WEBHOOK_URL}/init_conversation"

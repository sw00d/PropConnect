from unittest.mock import patch

from django.urls import reverse
from rest_framework import status

from companies.models import Company
from conversations.models import Vendor
from users.models import User
from ..utils import CkcAPITestCase


class VendorTests(CkcAPITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Company')
        self.user = User.objects.create(email='test@example.com', company=self.company)
        self.other_company = Company.objects.create(name='Other Company')
        self.other_user = User.objects.create(email='other@example.com', company=self.other_company)
        self.vendor = Vendor.objects.create(
            name="Test Vendor",
            vocation="plumber",
            number="1234567890",
            keywords=["test1", "test2"],
            active=True,
            has_opted_in=False,
            company=self.company,
        )
        self.url = reverse('vendors-detail', kwargs={'pk': self.vendor.pk})
        self.client.force_authenticate(self.user)

    def test_create_vendor(self):
        # Authenticate as a user from a different company
        self.client.force_authenticate(self.other_user)

        data = {
            "name": "New Vendor",
            "vocation": "Electrician",
            "number": "12086608828",
            "keywords": ["new1", "new2"],
            "active": True,
            "company": self.company.id,
        }

        # Try to create a vendor for a company that the user is not a part of
        response = self.client.post(reverse('vendors-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Re-authenticate as a user from the correct company and try again
        self.client.force_authenticate(self.user)
        response = self.client.post(reverse('vendors-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vendor.objects.filter(company=self.company).count(), 2)
        self.assertEqual(Vendor.objects.get(id=response.data['id']).name, 'New Vendor')

    def test_read_vendor(self):
        # Try to read vendor details as a user from a different company
        self.client.force_authenticate(self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Re-authenticate as a user from the correct company and try again
        self.client.force_authenticate(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Vendor')

    def test_toggle_vendor_archived(self):

        self.client.force_authenticate(self.user)
        list_res = self.client.get(reverse('vendors-list'))
        assert list_res.status_code == status.HTTP_200_OK
        assert list_res.data['count'] == 1

        response = self.client.patch(self.url, {'is_archived': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vendor.objects.get(pk=self.vendor.pk).is_archived, True)

        list_res = self.client.get(reverse('vendors-list'))
        assert list_res.status_code == status.HTTP_200_OK
        assert list_res.data['count'] == 0

    def test_update_vendor(self):
        # Try to update vendor details as a user from a different company
        self.client.force_authenticate(self.other_user)
        data = {"name": "Updated Vendor"}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Re-authenticate as a user from the correct company and try again
        self.client.force_authenticate(self.user)
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vendor.objects.get(pk=self.vendor.pk).name, 'Updated Vendor')

    @patch('conversations.views.send_message')
    def test_vendor_opt_in_via_text_yes(self, mock_send_message):
        # Set up POST data
        post_data = {
            'From': self.vendor.number,
            'To': '0987654321',  # some valid number
            'Body': 'yes'
        }

        # Send POST request
        response = self.client.post('/init_conversation/', post_data)  # adjust this URL to your project

        # Refresh vendor instance from database
        self.vendor.refresh_from_db()

        # Check that self.vendor has now opted in
        self.assertTrue(self.vendor.has_opted_in)

        # Check that send_message was called with correct arguments
        mock_send_message.assert_called_once_with(post_data['From'], post_data['To'],
                                                  "Thank you! You will now receive messages from tenants.")

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, 200)

    @patch('conversations.views.send_message')
    def test_vendor_opt_in_via_text_no(self, mock_send_message):
        # Set up POST data
        post_data = {
            'From': self.vendor.number,
            'To': '0987654321',  # some valid number
            'Body': 'no'
        }

        # Send POST request
        response = self.client.post('/init_conversation/', post_data)

        # Refresh vendor instance from database
        self.vendor.refresh_from_db()

        # Check that self.vendor has not opted in
        self.assertFalse(self.vendor.has_opted_in)

        # Check that send_message was called with correct arguments
        mock_send_message.assert_called_once_with(
            post_data['From'],
            post_data['To'],
            "Sounds good! You will not receive messages from any tenants. If you ever change your mind, feel free to respond 'yes' to this message."
        )

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, 200)






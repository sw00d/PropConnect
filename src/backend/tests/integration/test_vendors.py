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
            vocation="Plumber",
            number="1234567890",
            keywords=["test1", "test2"],
            active=True,
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
            "number": "0987654321",
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

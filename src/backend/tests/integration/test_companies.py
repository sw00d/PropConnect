# tests.py

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from djstripe.models import PaymentMethod, StripeModel

from companies.models import Company
from factories import UserFactory, CompanyFactory
from tests.utils import CkcAPITestCase
from users.models import User


class TestCompanies(CkcAPITestCase):

    def setUp(self):
        self.test_company = CompanyFactory()
        self.admin_user = UserFactory(is_staff=True, company=self.test_company)

    def test_create_company(self):
        url = reverse('company-list')
        data = {
            'name': 'New Company',
            'website': 'www.newcompany.com',
            'number_of_doors': 2,
            'street': '456 New St',
            'city': 'New City',
            'state': 'NS',
            'zip_code': '67890',
            'country': 'Newland',
            # 'payment_method': test_payment_method.id,
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.client.force_authenticate(self.admin_user)
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Company.objects.count() == 2
        assert Company.objects.get(name='New Company')

    def test_update_company(self):
        url = reverse('company-detail', kwargs={'pk': self.test_company.pk})
        data = {
            'name': 'Updated Company',
            'website': 'www.updatedcompany.com',
            'number_of_doors': 2,
            'street': '456 Updated St',
            'city': 'Updated City',
            'state': 'US',
            'zip_code': '67890',
            'country': 'Updatedland',
        }
        response = self.client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.client.force_authenticate(self.admin_user)
        response = self.client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        self.test_company.refresh_from_db()
        print(Company.objects.all(), self.test_company.__dict__)
        assert self.test_company.name == 'Updated Company'

    def test_get_company(self):
        url = reverse('company-detail', kwargs={'pk': self.test_company.pk})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.client.force_authenticate(self.admin_user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == self.test_company.name

# @pytest.fixture
# def api_client():
#     return APIClient()
#
#
# @pytest.fixture
# def authenticated_api_client(api_client):
#     user = User.objects.create_user(email='testuser@test.com', password='testpass')
#     api_client.login(email='testuser', password='testpass')
#     return api_client
#
#
# @pytest.mark.django_db
# def test_update_company(authenticated_api_client, test_company):
#     url = reverse('company-detail', kwargs={'pk': test_company.pk})
#     data = {
#         'name': 'Updated Company',
#         'website': 'www.updatedcompany.com',
#         'number_of_doors': 2,
#         'street': '456 Updated St',
#         'city': 'Updated City',
#         'state': 'US',
#         'zip_code': '67890',
#         'country': 'Updatedland',
#     }
#     response = authenticated_api_client.put(url, data, format='json')
#     assert response.status_code == status.HTTP_200_OK
#     test_company.refresh_from_db()
#     assert test_company.name == 'Updated Company'
#     assert test_company.website == 'www.updatedcompany.com'
#
#
# @pytest.fixture
# def test_company():
#     return Company.objects.create(
#         name='Test Company',
#         website='www.testcompany.com',
#         number_of_doors=1,
#         street='123 Test St',
#         city='Test City',
#         state='TS',
#         zip_code='12345',
#         country='Testland',
#         # payment_method=test_payment_method
#     )
#
#
# @pytest.mark.django_db




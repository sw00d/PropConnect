# tests.py
from unittest.mock import patch, MagicMock

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from commands.management.commands.generate_data import sync_stripe_product
from companies.models import Company
from factories import UserFactory, CompanyFactory
from settings.base import STRIPE_SECRET_KEY
from tests.utils import CkcAPITestCase
from users.models import User


class TestCompanies(CkcAPITestCase):

    def setUp(self):
        self.test_company = CompanyFactory()
        self.admin_user = UserFactory(is_staff=True, company=self.test_company)
        sync_stripe_product()

    def test_update_company(self):
        url = reverse('company-detail', kwargs={'pk': self.test_company.pk})
        data = {
            'name': 'Updated Company',
            'website': 'www.updatedcompany.com',
            'number_of_doors': 2,
            'street_1': '456 Updated St',
            'street_2': 'Apt 1',
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

        assert self.test_company.name == 'Updated Company'

    @patch('stripe.Customer.create')
    @patch('stripe.Customer.retrieve')
    @patch('stripe.Subscription.create')
    @patch('djstripe.models.Customer.get_or_create')
    @patch('djstripe.models.PaymentMethod.sync_from_stripe_data')
    def test_company_signup(self, sync_from_stripe_data_mock, get_or_create_mock, subscription_create_mock, retrieve_mock, create_mock):
        # Mock the payment_method
        payload = {'payment_method_id': 'pm_test'}

        # Mock the returned Stripe customer
        invoice_settings_mock = MagicMock(default_payment_method='pm_test')
        stripe_customer_mock = MagicMock(id='cus_test', invoice_settings=invoice_settings_mock)
        create_mock.return_value = stripe_customer_mock
        retrieve_mock.return_value = stripe_customer_mock

        # Mock the get_or_create method to return a (Customer, created) tuple
        customer_mock = MagicMock()
        get_or_create_mock.return_value = (customer_mock, True)

        # Mock the PaymentMethod.sync_from_stripe_data method
        sync_from_stripe_data_mock.return_value = MagicMock()

        url = reverse('company-list')
        data = {
            'name': 'New Company',
            'website': 'www.newcompany.com',
            'number_of_doors': 2,
            'street_1': '456 New St',
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

        # Get the ID of the newly created company from the response
        company_id = self.admin_user.company.id

        # Patch the company with the payment method ID
        patch_url = reverse('company-detail', kwargs={'pk': company_id})
        patch_data = payload

        patch_response = self.client.patch(patch_url, patch_data, format='json')
        assert patch_response.status_code == status.HTTP_200_OK

        assert Company.objects.get(id=company_id).stripe_customer_id is not None
        assert Company.objects.get(id=company_id).stripe_subscription_id is None

        subscription_create_mock.return_value = MagicMock(id='sub_test')  # Mock the returned Stripe Subscription

        # Call the finalize_signup action
        signup_url = reverse('company-finalize-signup', kwargs={'pk': company_id})
        signup_response = self.client.post(signup_url)
        assert signup_response.status_code == status.HTTP_200_OK

        assert Company.objects.get(id=company_id).stripe_subscription_id is not None

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

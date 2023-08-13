# tests.py
from unittest.mock import patch, MagicMock

import stripe
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from commands.management.commands.generate_data import sync_stripe_product
from companies.models import Company
from factories import UserFactory, CompanyFactory
from tests.utils import CkcAPITestCase


class TestCompanies(CkcAPITestCase):

    # @patch.object(stripe.Subscription, 'retrieve')
    def setUp(self):
        # Mock subscription
        # mock_subscription = MagicMock()
        # mock_retrieve.return_value = mock_subscription
        self.test_company = CompanyFactory(current_subscription=None)
        self.admin_user = UserFactory(is_staff=True, company=self.test_company)
        self.normal_user = UserFactory()
        sync_stripe_product()

    @patch.object(stripe.Subscription, 'retrieve')
    def test_get_company(self, mock_subscription_retrieve):
        mock_subscription = MagicMock()
        mock_subscription_retrieve.return_value = mock_subscription
        company = self.test_company
        url = reverse('companies-detail', kwargs={'pk': company.pk})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        self.normal_user.company = company
        self.normal_user.save()

        self.client.force_authenticate(self.normal_user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # assert response.data['name'] == self.test_company.name

    # To create a test instance of Company where current_subscription returns True:
    def test_company_with_subscription(self):
        with patch('stripe.Subscription.retrieve', return_value=MagicMock()):
            company = CompanyFactory()
            assert company.current_subscription is not None

    def test_update_company(self):
        url = reverse('companies-detail', kwargs={'pk': self.test_company.pk})
        data = {
            'name': 'Updated Company',
            'website': 'www.updatedcompany.com',
            'number_of_doors': '50-200',
            'zip_code': '67890',
        }
        response = self.client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        assert self.test_company.name != 'Updated Company'
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
    def test_company_signup(
        self,
        sync_from_stripe_data_mock,
        get_or_create_mock,
        subscription_create_mock,
        retrieve_mock,
        create_mock
    ):
        self.admin_user.company = None
        self.admin_user.save()

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

        url = reverse('companies-list')
        data = {
            'name': 'New Company',
            'website': 'www.newcompany.com',
            'number_of_doors': '1-50',
            'zip_code': '67890',
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert self.admin_user.company is None
        self.client.force_authenticate(self.admin_user)
        response = self.client.post(url, data, format='json')

        self.admin_user.refresh_from_db()
        assert self.admin_user.company is not None

        assert response.status_code == status.HTTP_201_CREATED
        assert Company.objects.count() == 2
        assert Company.objects.get(name='New Company')
        assert Company.objects.get(name='New Company').point_of_contact == self.admin_user

        # Get the ID of the newly created company from the response
        company_id = self.admin_user.company.id

        # Patch the company with the payment method ID
        patch_url = reverse('companies-detail', kwargs={'pk': company_id})
        patch_data = payload

        patch_response = self.client.patch(patch_url, patch_data, format='json')
        assert patch_response.status_code == status.HTTP_200_OK

        assert Company.objects.get(id=company_id).current_subscription is None

        subscription_mock_response = {}

        subscription_create_mock.return_value = subscription_mock_response  # Mock the returned Stripe Subscription
        stripe_customer_dict = stripe_data = { }

        create_mock.return_value = stripe_customer_dict
        retrieve_mock.return_value = stripe_customer_dict

        # TODO FIX THIS TEST
        # Call the finalize_signup action
        # TODO     @patch('conversations.tasks.purchase_phone_number_util') cause we don't wanna buy a number every test run
        # signup_url = reverse('companies-finalize-signup', kwargs={'pk': company_id})

        # signup_response = self.client.post(signup_url)
        # assert signup_response.status_code == status.HTTP_200_OK
        # assert Company.objects.get(id=company_id).current_subscription is not None

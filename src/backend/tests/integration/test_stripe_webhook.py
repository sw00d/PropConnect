import json
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch, MagicMock

from companies.models import Company
from companies.views import handle_subscription_deleted, handle_subscription_updated
from factories import CompanyFactory, UserFactory, CustomerFactory
from tests.utils import CkcAPITestCase
from djstripe.models import Event, Subscription
from unittest.mock import patch


class StripeWebhookTestCase(CkcAPITestCase):
    def setUp(self):
        self.user = UserFactory(is_staff=True)
        self.company = CompanyFactory()  # This should create a Customer and Subscription as well

    def test_handle_subscription_updated(self):
        # Create a mock customer, subscription, and company
        subscription = Subscription.objects.create(
            id='sub_test',
            current_period_end=(timezone.now() + timedelta(days=30)).isoformat(),
            current_period_start=timezone.now().isoformat(),
            customer=self.company.stripe_customer,
        )
        company = Company.objects.create(current_subscription=subscription)

        # Create a mock event
        event = MagicMock(spec=Event)
        event.data = {"object": {
            'id': 'sub_test',
            'current_period_end': (timezone.now() + timedelta(days=30)).isoformat(),
            'current_period_start': timezone.now().isoformat(),
            'customer': self.company.stripe_customer.id,
        }}

        # Patch the sync_from_stripe_data method to return our existing subscription
        with patch.object(Subscription, 'sync_from_stripe_data') as mock_sync:
            mock_sync.return_value = subscription

            # Call the handler
            handle_subscription_updated(event)

        # Refresh the company from the database
        company.refresh_from_db()

        # Verify the subscription was updated
        assert company.current_subscription == subscription

    def test_handle_subscription_deleted(self):
        # ----------------

        # ----------------
        # Create a mock customer, subscription, and company
        subscription = Subscription.objects.create(
            id='sub_test',
            current_period_end=(timezone.now() + timedelta(days=30)).isoformat(),
            current_period_start=timezone.now().isoformat(),
            customer=self.company.stripe_customer,
        )
        company = Company.objects.create(current_subscription=subscription,
                                         stripe_customer=self.company.stripe_customer)

        # Create a mock event
        event = MagicMock(spec=Event)
        event.data = {"object": {"id": 'sub_test'}}

        assert company.current_subscription is not None

        # Call the handler
        handle_subscription_deleted(event)

        # Refresh the company from the database
        company.refresh_from_db()

        # Verify the subscription was removed
        assert company.current_subscription is None

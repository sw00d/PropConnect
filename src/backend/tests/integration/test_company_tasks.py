from unittest.mock import patch, Mock
from datetime import datetime, timedelta

from django.utils import timezone
from freezegun import freeze_time

from companies.models import Company, Transaction
from companies.tasks import charge_companies_for_conversations, get_last_month_range
from conversations.models import Conversation
from factories import TenantFactory, CompanyFactory, ConversationFactory, SubscriptionFactory
from tests.utils import CkcAPITestCase


class TestCompanyTasks(CkcAPITestCase):

    def tearDown(self):
        # Return 'date_created' to its original state
        Conversation._meta.get_field('date_created').auto_now_add = True

    @patch('stripe.Customer.retrieve')
    @patch('djstripe.models.Charge')
    def test_charge_companies_for_conversations(self, mock_charge, mock_customer_retrieve):
        Conversation._meta.get_field('date_created').auto_now_add = False

        freeze_date = "2023-08-15"
        with freeze_time(freeze_date):
            # Create a company with conversation in the previous month
            active_subscription = SubscriptionFactory()
            company = CompanyFactory(current_subscription=active_subscription)

            conversation_date = datetime.strptime(freeze_date, "%Y-%m-%d") - timedelta(days=30)  # 30 days ago (last_month)
            for i in range(10):
                ConversationFactory(company=company, date_created=conversation_date)

            conversation_date = datetime.strptime(freeze_date, "%Y-%m-%d") - timedelta(days=4)  # 4 days ago (this month)
            for i in range(5):
                ConversationFactory(company=company, date_created=conversation_date)

            mock_customer_retrieve.return_value = Mock()

            mock_charge.objects.create.return_value = Mock(invoice_id="1234")

            # Call the task
            charge_companies_for_conversations()

            assert Transaction.objects.count() == 1
            assert Transaction.objects.first().amount == 4
            assert Transaction.objects.first().charge_date == timezone.now()
            assert Transaction.objects.first().company == company
            
    def test_get_last_month_range(self):
        # Freeze time to a specific date
        with freeze_time("2023-08-15"):
            start, end = get_last_month_range()

        # Assert the results
        assert start == timezone.datetime(2023, 7, 1, tzinfo=timezone.utc)
        assert end == timezone.datetime(2023, 7, 31, tzinfo=timezone.utc)

        # Freeze time to a specific date where the previous month has less than 31 days
        with freeze_time("2023-09-01"):
            start, end = get_last_month_range()

        # Assert the results
        assert start == timezone.datetime(2023, 8, 1, tzinfo=timezone.utc)
        assert end == timezone.datetime(2023, 8, 31, tzinfo=timezone.utc)

        # Freeze time to a specific date where the previous month is February in a non-leap year
        with freeze_time("2023-03-01"):
            start, end = get_last_month_range()

        # Assert the results
        assert start == timezone.datetime(2023, 2, 1, tzinfo=timezone.utc)
        assert end == timezone.datetime(2023, 2, 28, tzinfo=timezone.utc)

        # Freeze time to a specific date where the previous month is February in a leap year
        with freeze_time("2024-03-01"):
            start, end = get_last_month_range()

        # Assert the results
        assert start == timezone.datetime(2024, 2, 1, tzinfo=timezone.utc)
        assert end == timezone.datetime(2024, 2, 29, tzinfo=timezone.utc)

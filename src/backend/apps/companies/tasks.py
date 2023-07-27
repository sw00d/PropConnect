import logging
from calendar import monthrange
from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta

from conversations.models import Conversation
from settings import celery_app

from django.utils import timezone

from django.db.models import Count, Q

from companies.models import Company, Transaction
from djstripe.models import Customer, Charge
import stripe

logger = logging.getLogger(__name__)


def get_last_month_range():
    """
    Returns the first and last day of the previous month
    """
    today = timezone.now()
    last_month = today - relativedelta(months=1)
    _, num_days = monthrange(last_month.year, last_month.month)
    first_of_prev_month = last_month.replace(day=1)
    last_of_prev_month = last_month.replace(day=num_days)
    return first_of_prev_month, last_of_prev_month


@celery_app.task
def charge_companies_for_conversations():
    # Get first and last day of previous month
    first_of_prev_month, last_of_prev_month = get_last_month_range()

    # Get companies with conversations
    companies = [company for company in Company.objects.all() if company.has_active_subscription]

    for company in companies:
        convos_last_month = company.conversations.all().filter(
            Q(
                date_created__gte=first_of_prev_month,
                date_created__lt=last_of_prev_month
            )
        )

        # Get customer and conversation count
        customer = stripe.Customer.retrieve(company.customer_stripe_id)
        num_convos = convos_last_month.count()

        # Calculate amount
        amount = num_convos * 0.4  # 40 cents per conversation

        try:
            logger.info(f"Charging {company} ${amount} for {num_convos} conversations from day: {first_of_prev_month} to day: {last_of_prev_month}")

            # Create charge
            charge = Charge.objects.create(
                amount=amount * 100,
                currency="usd",
                customer=customer,
                description=f"Conversations starting on {first_of_prev_month:%B %Y} and ending {last_of_prev_month:%B %Y}"
            )

            # Create Transaction object
            Transaction.objects.create(
                company=company,
                amount=amount,
                charge_date=timezone.now(),
                successful=True,
                invoice_id=charge.invoice_id
            )

        except Exception as e:
            logger.error(f"Error charging {company} for conversations: {e}")
            # Handle charge failure
            Transaction.objects.create(
                company=company,
                amount=amount,
                charge_date=timezone.now(),
                successful=False
            )

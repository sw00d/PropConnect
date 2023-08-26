import stripe
from twilio.rest import Client
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from conversations.models import PhoneNumber
from conversations.tasks import purchase_phone_number_util
from conversations.utils import send_message
from stripe_features.models import Product
from .models import Company
from .serializers import CompanyCreateSerializer, CompanyUpdateSerializer
from djstripe import webhooks
from djstripe.models import Subscription

from settings.base import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, WEBHOOK_URL, DEFAULT_TWILIO_NUMBER
import logging

twilio_auth_token = TWILIO_AUTH_TOKEN
twilio_sid = TWILIO_ACCOUNT_SID
logger = logging.getLogger(__name__)


class CompanyViewSet(viewsets.ModelViewSet):
    # queryset = Company.objects.all()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Company.objects.filter(id=self.request.user.company.id)
        return Company.objects.none()  # Return an empty queryset for anonymous users

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create']:
            return CompanyCreateSerializer
        return CompanyUpdateSerializer

    @action(detail=True, methods=['post'])
    def finalize_signup(self, request, pk=None):
        company = Company.objects.get(id=pk)

        plan = Product.objects.get(name='Basic Plan')
        price = plan.prices.first()  # Fetch the first price of the basic plan product

        customer = stripe.Customer.retrieve(company.customer_stripe_id)

        stripe_subscription = stripe.Subscription.create(
            customer=customer,
            items=[
                {
                    "price": price.stripe_price_id,
                },
            ],
            trial_period_days=7  # This offers a 7-day free trial
        )

        djstripe_subscription = Subscription.sync_from_stripe_data(stripe_subscription)
        company.current_subscription = djstripe_subscription

        client = Client(twilio_sid, twilio_auth_token)
        number_to_purchase = client.available_phone_numbers("US").toll_free.list(limit=3)[0]
        # Fetch all purchased phone numbers
        numbers = client.incoming_phone_numbers.list(limit=100)
        # TODO once we get more than 100 toll free numbers, we'll have to revise this I think

        # Filter for toll-free numbers (assuming they start with '+18' for North America)
        toll_free_numbers = [number.phone_number for number in numbers if number.phone_number.startswith('+18')]
        available_toll_free_number = None

        for toll_free_number in toll_free_numbers:
            if not Company.objects.filter(assistant_phone_number=toll_free_number):
                available_toll_free_number = toll_free_number
                break

        if 'samote.wood' in self.request.user.email or self.request.user.is_superuser:
            logger.info(f"Using admin number: {DEFAULT_TWILIO_NUMBER}")
            print(f"Using admin number: {DEFAULT_TWILIO_NUMBER}")
            company.assistant_phone_number = DEFAULT_TWILIO_NUMBER
        elif available_toll_free_number:
            company.assistant_phone_number = available_toll_free_number
            phone_num_obj = PhoneNumber.objects.get_or_create(number=available_toll_free_number)
            phone_num_obj.is_base_number = True
            phone_num_obj.company = company
            phone_num_obj.save()
        else:
            logger.info(f"Purchasing new company number: {number_to_purchase.phone_number}")
            purchase_phone_number_util(number_to_purchase.phone_number, "/init_conversation/", 'toll-free')
            company.assistant_phone_number = number_to_purchase.phone_number
            PhoneNumber.objects.create(number=number_to_purchase.phone_number, is_base_number=True, company=company)

        company.save()

        # Just alerting Sam that a new conversation has started, and he should probably go look at it
        send_message('+12086608828', DEFAULT_TWILIO_NUMBER,
                     f"New company signed up {company.name} with phone number {company.assistant_phone_number}")
        return Response({"message": "Signup finalized."}, status=status.HTTP_200_OK)


@webhooks.handler('customer.subscription.deleted')
def handle_subscription_deleted(event, **kwargs):
    # Process the event
    subscription = event.data["object"]

    # Get the associated company
    company = Company.objects.filter(current_subscription__id=subscription['id']).first()
    if company:
        company.current_subscription = None  # Or set it to "cancelled" or a similar status
        company.save()


@webhooks.handler('customer.subscription.updated')
def handle_subscription_updated(event, **kwargs):
    # TODO test this. Does it work?

    # Process the event
    subscription = event.data["object"]

    # Get the associated company
    company = Company.objects.filter(current_subscription__id=subscription['id']).first()

    if company:
        # With dj-stripe, the object data can be converted to the local model instance using .api_retrieve()
        local_subscription = Subscription.sync_from_stripe_data(subscription)
        company.current_subscription = local_subscription
        company.save()


import stripe
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from stripe_features.models import Product
from .models import Company
from .serializers import CompanyCreateSerializer, CompanyUpdateSerializer
from djstripe import webhooks
from djstripe.models import Subscription

from settings.base import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, WEBHOOK_URL, DEFAULT_TWILIO_NUMBER
import logging

from .utils import assign_company_assistant_number

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

        if not company.assistant_phone_number:
            assign_company_assistant_number(self.request, company=company)

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


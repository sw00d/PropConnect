import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from stripe import Webhook

from settings.base import STRIPE_SECRET_KEY
from stripe_features.models import Product
from .models import Company
from .serializers import CompanyCreateSerializer, CompanyUpdateSerializer
from djstripe import webhooks
from djstripe.models import Subscription



class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.request.user.company
        return Company.objects.none()  # Return an empty queryset for anonymous users

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        # if self.action in ['create', 'update', 'partial_update']:
        #     self.permission_classes = [IsAuthenticated]
        # else:
        #     self.permission_classes = [AllowAny]
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

        subscription = stripe.Subscription.create(
            customer=company.stripe_customer.id,
            items=[
                {
                    "price": price.stripe_price_id,
                },
            ]
        )
        company.current_subscription = subscription
        company.save()

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


@webhooks.handler('subscription.updated')
def handle_subscription_updated(event, **kwargs):
    print('fire')
    # # Process the event
    # subscription = event.data["object"]
    #
    # # Get the associated company
    # company = Company.objects.filter(current_subscription__id=subscription['id']).first()
    # if company:
    #     # With dj-stripe, the object data can be converted to the local model instance using .api_retrieve()
    #     local_subscription = Subscription.sync_from_stripe_data(subscription)
    #     company.current_subscription = local_subscription
    #     company.save()


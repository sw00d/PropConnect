import stripe
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from stripe_features.models import Product
from .models import Company
from .serializers import CompanyCreateSerializer, CompanyUpdateSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Company.objects.filter(id=self.request.user.company.id)
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
            customer=company.stripe_customer_id,
            items=[
                {
                    "price": price.stripe_price_id,
                },
            ]
        )
        company.stripe_subscription_id = subscription.id
        company.save()

        return Response({"message": "Signup finalized."}, status=status.HTTP_200_OK)

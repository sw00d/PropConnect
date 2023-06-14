from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Company
from .serializers import CompanyCreateSerializer, CompanyUpdateSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()

    def get_queryset(self):
        return Company.objects.filter(id=self.request.user.company.id)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create']:
            return CompanyCreateSerializer
        return CompanyUpdateSerializer

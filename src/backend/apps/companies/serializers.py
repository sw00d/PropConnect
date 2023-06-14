# serializers.py

from rest_framework import serializers
from .models import Company


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'name',
            'website',
            'number_of_doors',
            'street',
            'city',
            'state',
            'zip_code',
            'country'
        )

    def create(self, validated_data):
        return Company.objects.create(**validated_data)


class CompanyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'number_of_doors',
            'payment_method',
            'street',
            'city',
            'state',
            'zip_code',
            'country'
        )

    def update(self, instance, validated_data):
        instance.number_of_doors = validated_data.get('number_of_doors', instance.number_of_doors)
        instance.payment_method = validated_data.get('payment_method', instance.payment_method)
        instance.street = validated_data.get('street', instance.street)
        instance.city = validated_data.get('city', instance.city)
        instance.state = validated_data.get('state', instance.state)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)
        instance.country = validated_data.get('country', instance.country)
        instance.save()
        return instance

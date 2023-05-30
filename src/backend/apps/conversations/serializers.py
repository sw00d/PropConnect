from rest_framework import serializers
from .models import Vendor, Tenant, Conversation, Message, PhoneNumber


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    tenant = TenantSerializer(read_only=True)
    vendor = VendorSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = ('id', 'tenant', 'vendor', 'date_created', 'is_active', 'messages')


class PhoneNumberSerializer(serializers.ModelSerializer):
    most_recent_conversation = ConversationSerializer(read_only=True)

    class Meta:
        model = PhoneNumber
        fields = ('id', 'number', 'most_recent_conversation', 'is_base_number')

from rest_framework import serializers
# from rest_framework.relations import PrimaryKeyRelatedField

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


class PhoneNumberSerializer(serializers.ModelSerializer):
    # most_recent_conversation = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PhoneNumber
        fields = ('id', 'number')


class ConversationSerializer(serializers.ModelSerializer):
    assistant_messages = MessageSerializer(many=True, read_only=True)
    vendor_messages = MessageSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    tenant = TenantSerializer(read_only=True)
    vendor = VendorSerializer(read_only=True)
    twilio_number = PhoneNumberSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = (
            'id',
            'tenant',
            'vendor',
            'date_created',
            'is_active',
            'assistant_messages',
            'vendor_messages',
            'twilio_number',
            'messages'
        )


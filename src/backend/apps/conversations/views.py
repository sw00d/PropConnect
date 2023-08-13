import logging
from sys import argv

from django.utils.timezone import now

from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet

from twilio.twiml.messaging_response import MessagingResponse
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny

from conversations.utils import handle_assistant_conversation, play_the_middle_man_util, send_message

from .models import Conversation, Message, Vendor, PhoneNumber
from .serializers import ConversationDetailSerializer, ConversationListSerializer, VendorSerializer
from .tasks import start_vendor_tenant_conversation

logger = logging.getLogger(__name__)


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100
    page_size_query_param = "page_size"


class VendorViewSet(ModelViewSet):
    pagination_class = CustomPageNumberPagination
    serializer_class = VendorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Vendor.objects.filter(company=self.request.user.company, is_archived=False).order_by('id')

    #     overwrite create
    def create(self, request, *args, **kwargs):
        if not request.user.company.id == int(request.data.get('company')):
            return Response({'error': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        response = super().create(request, *args, **kwargs)

        send_message(
            request.data.get('number'),
            request.user.company.assistant_phone_number,
            f"{request.user.company.name} has included you as a service vendor in their automated maintenance "
            f"management system, PropConnect. To confirm and start receiving direct messages from tenants, please reply with 'YES'."
            # f" If you need more information, you can learn more here: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )

        return response

    @action(detail=True, methods=['post'])
    def resend_opt_in(self, request, pk=None):
        vendor = self.get_object()

        send_message(
            vendor.number,
            request.user.company.assistant_phone_number,
            f"We noticed you haven't responded to our earlier message. {request.user.company.name} has enlisted you as a service "
            f"vendor for their property management system. To accept and start receiving tenant communications, please reply 'YES'. "
            f"Remember, this will enable faster and more efficient service requests for all involved. Thank you!"
        )
        return Response({'status': 'opt in message sent'})


class ConversationViewSet(ModelViewSet):
    pagination_class = CustomPageNumberPagination
    permission_classes([AllowAny])

    def get_queryset(self):
        return Conversation.objects.filter(company=self.request.user.company, company__isnull=False).order_by(
            '-date_created')

    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        else:
            return ConversationDetailSerializer

    @action(detail=True, methods=['post'])
    def set_last_viewed(self, request, pk=None):
        conversation = self.get_object()
        conversation.last_viewed = now()
        conversation.save()

        return Response({'status': 'last_viewed time updated'})

    @action(detail=True, methods=['post'])
    def assign_vendor(self, request, pk=None):
        conversation = self.get_object()
        try:
            conversation.vendor = Vendor.objects.get(id=request.data.get('vendor'))
            conversation.tenant_intro_message = request.data.get('tenant_intro_message')
            conversation.vendor_intro_message = request.data.get('vendor_intro_message')
            conversation.save()
            if 'pytest' in argv[0]:
                print('pytest detected. Using test credentials.')
                start_vendor_tenant_conversation(conversation.id, conversation.vendor.id)
            else:
                start_vendor_tenant_conversation.delay(conversation.id, conversation.vendor.id)
        except Vendor.DoesNotExist:
            raise ValidationError({"error": "Vendor not found."})
        conversation.save()

        return Response({'status': 'Vendor assigned to conversation.'})

    @action(detail=True, methods=['post'])
    def send_admin_message_to_tenant(self, request, *args, **kwargs):
        # This is so admin can inject messages into the conversation
        message_body = request.data.get('message_body')

        if not message_body:
            return Response({'error': 'Message_body must be provided.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # from_number = self.get_object().twilio_number.number
        conversation = self.get_object()
        from_number = conversation.company.assistant_phone_number
        tenant_number = conversation.tenant.number
        message = Message.objects.create(
            message_content=message_body,
            role="admin_to_tenant",
            conversation=conversation,
            sender_number=from_number
        )

        conversation.point_of_contact_has_interjected = True
        conversation.save()

        try:
            logger.info(f"Sending admin message to conversation ({conversation}) from with body: {message_body}")
            send_message(tenant_number, from_number, message_body, message_object=message)
            return Response({'status': 'Message sent.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def send_admin_message_to_group(self, request, *args, **kwargs):
        # This is so admin can inject messages into the conversation
        message_body = request.data.get('message_body')

        if not message_body:
            return Response({'error': 'Message_body must be provided.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # from_number = self.get_object().twilio_number.number
        from_number = PhoneNumber.objects.get(most_recent_conversation=self.get_object()).number
        tenant_number = self.get_object().tenant.number
        vendor_number = self.get_object().vendor.number
        message = Message.objects.create(
            message_content=message_body,
            role="admin",
            conversation=self.get_object(),
            sender_number=from_number
        )

        try:
            logger.info(f"Sending admin message to conversation ({self.get_object()}) with body: {message_body}")
            send_message(tenant_number, from_number, message_body, message_object=message)
            send_message(vendor_number, from_number, message_body, message_object=message)
            return Response({'status': 'Message sent.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# TODO: Handle errors from twilio and log somehow. also change webhook url in twilio existing nums
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def play_the_middle_man(request):
    play_the_middle_man_util(request)
    return HttpResponse()


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def init_conversation(request):
    # ==================== Handle vendor opt in texts ================================
    # TODO: Use a different number for this in the future?
    from_number = request.POST.get('From', None)
    to_number = request.POST.get('To', None)
    body = request.POST.get('Body', '')

    vendor_opting_in = Vendor.objects.filter(number=from_number, has_opted_in=False)
    # TODO TEST THIS
    if vendor_opting_in.exists():
        # Check if number is a vendor's number AND the vendor has not opted in yet
        vendor = vendor_opting_in.first()

        yes_synonyms = ['yes', 'yep', 'yeah', 'yup', 'sure', 'absolutely', 'definitely', 'certainly', 'yea',
                        'affirmative', 'uh-huh', 'indeed', 'of course', 'true']
        no_synonyms = ['no', 'nope', 'nah', 'negative', 'not at all', 'nay', 'absolutely not', 'by no means',
                       'certainly not', 'definitely not']
        if any(word in body.lower() for word in yes_synonyms):
            vendor.has_opted_in = True
            vendor.active = True
            vendor.save()
            # Reply to vendor
            send_message(from_number, to_number, "Thank you! You will now receive messages from tenants.")
        elif any(word in body.lower() for word in no_synonyms):
            # Reply to vendor
            send_message(from_number, to_number,
                         "Sounds good! You will not receive messages from any tenants. If you ever change your mind, feel free to respond 'yes' to this message.")

        return HttpResponse()

    # ==================== Handle normal conversation between tenant and GPT ================================
    message = handle_assistant_conversation(request)

    if not message:
        # If we hit GPT, we manually send message instead of returning from this view
        return HttpResponse()
    else:
        # When we don't hit GPT, we just return a string from the view and it sends to the user
        twiml_response = MessagingResponse()
        twiml_response.message(message)

        response = HttpResponse(str(twiml_response), content_type='text/xml')
        return response

import logging
from django.utils.timezone import now

from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from twilio.twiml.messaging_response import MessagingResponse
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny

from conversations.utils import handle_assistant_conversation, play_the_middle_man_util, send_message
from users import permissions
from .models import Conversation, Message, Vendor, PhoneNumber
from .serializers import ConversationDetailSerializer, ConversationListSerializer, VendorSerializer

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
        return Vendor.objects.filter(company=self.request.user.company).order_by('id')

#     overwrite create
    def create(self, request, *args, **kwargs):
        if not request.user.company.id == int(request.data.get('company')):
            return Response({'error': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        response = super().create(request, *args, **kwargs)
        return response


class ConversationViewSet(ModelViewSet):
    pagination_class = CustomPageNumberPagination
    permission_classes([AllowAny])

    def get_queryset(self):
        return Conversation.objects.filter(company=self.request.user.company, company__isnull=False).order_by('-date_created')

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
    def send_admin_message(self, request, *args, **kwargs):
        # This is so admin can inject messages into the conversation
        message_body = request.data.get('message_body')

        if not message_body:
            return Response({'error': 'Message_body must be provided.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # from_number = self.get_object().twilio_number.number
        from_number = PhoneNumber.objects.get(most_recent_conversation=self.get_object())
        tenant_number = self.get_object().tenant.number
        vendor_number = self.get_object().vendor.number
        Message.objects.create(
            message_content=message_body,
            role="admin",
            conversation=self.get_object(),
            sender_number=from_number
        )

        try:
            logger.info(f"Sending admin message to conversation ({self.get_object()}) from with body: {message_body}")
            send_message(tenant_number, from_number, message_body)
            send_message(vendor_number, from_number, message_body)
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

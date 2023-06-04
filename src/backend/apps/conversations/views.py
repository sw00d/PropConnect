import logging
from rest_framework import status
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from twilio.twiml.messaging_response import MessagingResponse
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny

from conversations.utils import init_conversation_util, play_the_middle_man_util, send_message
from .models import Conversation, Message
from .serializers import ConversationSerializer

logger = logging.getLogger(__name__)


class ConversationViewSet(ModelViewSet):
    # TODO: add pagination
    # TODO: make list serlializer different from detail serializer
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes([IsAdminUser])

    @action(detail=True, methods=['post'])
    def send_admin_message(self, request, *args, **kwargs):
        # TODO TEST THIS
        # This is so admin can inject messages into the conversation

        message_body = request.data.get('message_body')

        if not message_body:
            return Response({'error': 'Message_body must be provided.'},
                            status=status.HTTP_400_BAD_REQUEST)

        from_number = self.get_object().twilio_number.number
        tenant_number = self.get_object().tenant.number
        vendor_number = self.get_object().vendor.number
        Message.objects.create(
            message_content=message_body,
            role="admin",
            conversation=self.get_object(),
            sender_number=from_number
        )

        try:
            print(f"Sending admin message to converation ({self.get_object()}) from with body: {message_body}")
            logger.info(f"Sending admin message to converation ({self.get_object()}) from with body: {message_body}")
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
    message = init_conversation_util(request)

    if not message:
        # If we hit GPT, we manually send message instead of returning from this view
        return HttpResponse()
    else:
        # When we don't hit GPT, we just return a string from the view and it sends to the user
        twiml_response = MessagingResponse()
        twiml_response.message(message)

        response = HttpResponse(str(twiml_response), content_type='text/xml')
        return response

from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet
from twilio.twiml.messaging_response import MessagingResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from conversations.utils import init_conversation_util, play_the_middle_man_util
from .models import Conversation
from .serializers import ConversationSerializer


class ConversationViewSet(ModelViewSet):
    # TODO: add pagination
    # TODO: make list serlializer different from detail serializer
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer


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
    twiml_response = MessagingResponse()
    twiml_response.message(message)

    response = HttpResponse(str(twiml_response), content_type='text/xml')
    return response

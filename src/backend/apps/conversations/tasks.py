from datetime import timedelta
from django.utils import timezone
from settings import celery_app
from .models import Conversation, Message


@celery_app.task
def set_old_conversations_to_not_active():
    three_days_ago = timezone.now() - timedelta(days=3)
    old_conversations = Message.objects.filter(time_sent__lt=three_days_ago).values('conversation').distinct()
    Conversation.objects.filter(id__in=old_conversations, is_active=True).update(is_active=False)

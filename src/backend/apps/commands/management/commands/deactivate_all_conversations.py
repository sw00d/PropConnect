from django.core.management.base import BaseCommand

from conversations.tasks import set_old_conversations_to_not_active


class Command(BaseCommand):
    help = "Setting old conversations to not active to free up twilio numbers"

    def handle(self, *args, **kwargs):
        set_old_conversations_to_not_active(0)

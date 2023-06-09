from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q

import settings.base


class Vendor(models.Model):
    name = models.CharField(max_length=200)
    vocation = models.CharField(max_length=200, blank=True, null=True)  # plumber | electrician | etc.
    number = models.CharField(max_length=20)
    keywords = ArrayField(models.CharField(max_length=200))
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Tenant(models.Model):
    name = models.CharField(max_length=200, null=True)
    number = models.CharField(max_length=20)
    address = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name if self.name else self.number


class Conversation(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # set to false if no messages in 3 days

    def __str__(self):
        return f"Conversation ({self.pk}) between {self.tenant} and vendor {self.vendor}"

    @property
    def assistant_messages(self):
        # TODO Test these
        from .models import Message  # Replace with your actual Message module
        DEFAULT_TWILIO_NUMBER = settings.base.DEFAULT_TWILIO_NUMBER  # Replace with your actual default twilio number
        return Message.objects.filter(
            Q(receiver_number=DEFAULT_TWILIO_NUMBER) | Q(sender_number=DEFAULT_TWILIO_NUMBER),
            conversation=self
        )

    @property
    def vendor_messages(self):
        # TODO Test these
        from .models import Message  # Replace with your actual Message module
        return Message.objects.filter(
            Q(sender_number=self.vendor.number) |
            (Q(sender_number=self.tenant.number) & Q(receiver_number=self.vendor.number)) |
            Q(role='admin'),
            conversation=self
        )


class MediaMessageContent(models.Model):
    MEDIA_TYPES = (
        ('image', 'image'),
        ('video', 'video'),
        ('other', 'other'),
    )
    message = models.ForeignKey(
        'Message',
        related_name='media_message_contents',
        on_delete=models.CASCADE,
    )
    media_url = models.URLField(null=True, blank=True)
    media_type = models.CharField(max_length=200, null=True, blank=True, choices=MEDIA_TYPES)


class Message(models.Model):
    # TODO add failed field for failed deliveries
    sender_number = models.CharField(max_length=20, null=False,
                                     blank=False)  # can be used to identify the sender model based off of conversation
    receiver_number = models.CharField(max_length=20, null=False, blank=False)
    time_sent = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=200)  # user | assistant | system | admin
    message_content = models.TextField()  # renaming 'content' to 'message_content' to avoid confusion
    conversation = models.ForeignKey(
        'Conversation',
        related_name='messages',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        # Return first 50 characters of message content
        return f"{self.role} message ({self.pk}): {self.message_content[:50]}"


class PhoneNumber(models.Model):
    number = models.CharField(max_length=17, blank=True)
    most_recent_conversation = models.OneToOneField(
        Conversation,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='twilio_number'
    )
    # this will be True for the main number that talks to GPT and initializes convo
    is_base_number = models.BooleanField(default=False)

    def __str__(self):
        return self.number

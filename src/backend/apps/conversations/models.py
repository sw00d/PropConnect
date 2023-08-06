from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import Q

import settings.base
from companies.models import Company


class Vendor(models.Model):
    name = models.CharField(max_length=200)
    vocation = models.CharField(max_length=200, blank=True, null=True)  # plumber | electrician | etc.
    number = models.CharField(max_length=20)
    keywords = ArrayField(models.CharField(max_length=200), null=True, blank=True)  # currently unused
    active = models.BooleanField(default=False)
    company = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)
    has_opted_in = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Tenant(models.Model):
    name = models.CharField(max_length=200, null=True)
    number = models.CharField(max_length=20)
    address = models.CharField(max_length=200, null=True)
    company = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name if self.name else self.number


class Conversation(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, null=True, on_delete=models.SET_NULL)
    proposed_vendor = models.ForeignKey(Vendor, null=True, on_delete=models.SET_NULL, related_name="proposed_for_conversation")  # vendor that was last proposed by the assistant
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # set to false if no messages in 3 days
    last_viewed = models.DateTimeField(auto_now_add=True)  # last time the conversation was viewed by the admin
    company = models.ForeignKey(Company, null=True, related_name="conversations", on_delete=models.SET_NULL)
    vendor_detection_attempts = models.IntegerField(default=0)
    address = models.CharField(max_length=200, null=True)
    waiting_on_property_manager = models.BooleanField(default=False)
    needs_more_information = models.BooleanField(default=True)  # TODO Unused

    def __str__(self):
        return f"Conversation ({self.pk}) between {self.tenant} and vendor {self.vendor}"

    @property
    def has_new_activity(self):
        # see if there are any messages that have been sent since the last time the conversation was viewed
        return self.messages.filter(time_sent__gt=self.last_viewed).exists()

    @property
    def assistant_messages(self):
        # TODO Test these
        # TODO Convert to company number
        from .models import Message
        number = self.company.assistant_phone_number
        return Message.objects.filter(
            Q(receiver_number=number) | Q(sender_number=number) | Q(role='admin_to_tenant'),
            conversation=self
        )

    @property
    def vendor_messages(self):
        # TODO Test these
        from .models import Message
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
    date_sent = models.DateTimeField(auto_now_add=True)
    error_on_send = models.BooleanField(default=False)

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

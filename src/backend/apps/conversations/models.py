from django.db import models
from django.contrib.postgres.fields import ArrayField


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


class Message(models.Model):
    sender_number = models.CharField(max_length=20, null=False, blank=False)  # can be used to identify the sender model based off of conversation
    receiver_number = models.CharField(max_length=20, null=False, blank=False)
    time_sent = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=200)  # user | assistant | system
    message_content = models.TextField()  # renaming 'content' to 'message_content' to avoid confusion
    conversation = models.ForeignKey(
        'Conversation',
        related_name='messages',
        on_delete=models.CASCADE,
    )
    #  Eventually refactor to this probably
    # initial_conversation = models.ForeignKey(
    #     'Conversation',
    #     related_name='initial_messages',
    #     on_delete=models.CASCADE,
    # )
    # vendor_conversation = models.ForeignKey(
    #     'Conversation',
    #     related_name='vendor_conversation_messages',
    #     on_delete=models.CASCADE,
    # )


class PhoneNumber(models.Model):
    number = models.CharField(max_length=17, blank=True)
    most_recent_conversation = models.OneToOneField(Conversation, null=True, blank=True, on_delete=models.CASCADE)
    # this will be True for the main number that talks to GPT and initializes convo
    is_base_number = models.BooleanField(default=False)

    def __str__(self):
        return self.number

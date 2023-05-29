import openai
from django.http import HttpRequest

from commands.management.commands.generate_data import generate_vendors
from conversations.models import Vendor, Tenant, Conversation, Message
from conversations.utils import init_conversation_util, get_vendor_from_conversation, create_chat_completion
from tests.utils import CkcAPITestCase
from unittest.mock import patch


class TestGPTErrorCases(CkcAPITestCase):
    @patch('openai.ChatCompletion.create')
    def test_rate_limit_error_is_recursive(self, mock_create):
        # Arrange
        mock_create.side_effect = openai.error.RateLimitError('Rate limit error')
        mock_create.side_effect = [openai.error.RateLimitError('Rate limit error'),
                                   {'choices': [{'message': {'content': 'Test content'}}]}]

        conversation = []  # add some test conversation messages here

        # Act
        res = create_chat_completion(conversation)
        assert res == 'Test content'


class TestVendorDetection(CkcAPITestCase):
    def setUp(self):
        # seed the db
        generate_vendors()
        tenant = Tenant.objects.create(number="1")  # Add necessary parameters
        vendor = Vendor.objects.first()  # Add necessary parameters
        self.conversation = Conversation.objects.create(tenant=tenant, vendor=vendor)

    def test_vendor_detection_returns_none(self):
        Message.objects.create(
            message_content='Hi there, my name is sam wood. 4861 conrad ave. I have a maintenance request.',
            role="user", conversation=self.conversation)

        self.conversation.refresh_from_db()
        response = get_vendor_from_conversation(self.conversation)

        assert response == None

    def test_vendor_detection_plumber(self):
        Message.objects.create(message_content='My toilet is broken.', role="user", conversation=self.conversation)
        Message.objects.create(message_content='Its leaking everywhere.', role="user", conversation=self.conversation)

        self.conversation.refresh_from_db()

        response = get_vendor_from_conversation(self.conversation)
        assert response == Vendor.objects.get(vocation='plumber')

    def test_vendor_detection_electrician(self):
        # Electrician
        Message.objects.create(message_content='My lights are flickering.', role="user", conversation=self.conversation)
        Message.objects.create(
            message_content='The light switch stays on and its a new bulb but it keeps flicking randomly', role="user",
            conversation=self.conversation)

        self.conversation.refresh_from_db()

        response = get_vendor_from_conversation(self.conversation)
        assert response == Vendor.objects.get(vocation='electrician')

    def test_vendor_detection_handyman(self):
        # Handyman
        Message.objects.create(message_content='Theres are going under my door and I think it needs something under there.', role="user", conversation=self.conversation)

        self.conversation.refresh_from_db()

        response = get_vendor_from_conversation(self.conversation)
        assert response == Vendor.objects.get(vocation='handyman')

    def test_vendor_detection_appliance_specialist(self):
        # Appliance Specialist
        Message.objects.create(message_content='My fridge is not cooling properly.', role="user",
                               conversation=self.conversation)

        self.conversation.refresh_from_db()

        response = get_vendor_from_conversation(self.conversation)
        assert response == Vendor.objects.get(vocation='appliance specialist')

    def test_vendor_detection_hvac(self):
        # HVAC Professional
        Message.objects.create(message_content='My AC isnt working', role="user",
                               conversation=self.conversation)

        self.conversation.refresh_from_db()

        response = get_vendor_from_conversation(self.conversation)
        assert response == Vendor.objects.get(vocation='air-condition specialist')

    def test_vendor_detection_locksmith(self):
        # Locksmith
        Message.objects.create(message_content='I am locked out of my house.', role="user",
                               conversation=self.conversation)

        self.conversation.refresh_from_db()

        response = get_vendor_from_conversation(self.conversation)
        assert response == Vendor.objects.get(vocation='locksmith')

    def test_vendor_detection_flooring_specialist(self):
        # Flooring Specialist
        Message.objects.create(
            message_content='Theres a huge crack in the tile in my kitchen and dining room.',
            role="user",
            conversation=self.conversation
        )

        self.conversation.refresh_from_db()

        response = get_vendor_from_conversation(self.conversation)
        assert response == Vendor.objects.get(vocation='flooring specialist')

    def test_vendor_detection_painter(self):
        # Painter
        Message.objects.create(
            message_content='I need to repaint my room.',
            role="user",
            conversation=self.conversation
        )

        self.conversation.refresh_from_db()

        response = get_vendor_from_conversation(self.conversation)
        assert response == Vendor.objects.get(vocation='painter')

    def test_vendor_detection_drywall_specialist(self):
        # Drywall Specialist
        Message.objects.create(
            message_content='There is a hole in my wall cause I ran into it with a baseball bat. I need it patched up.',
            role="user",
            conversation=self.conversation
        )

        self.conversation.refresh_from_db()

        response = get_vendor_from_conversation(self.conversation)
        assert response == Vendor.objects.get(vocation='drywall specialist')

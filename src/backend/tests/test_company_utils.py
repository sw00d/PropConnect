from companies.models import Company
from companies.utils import assign_company_assistant_number
from settings.base import DEFAULT_TWILIO_NUMBER
from tests.utils import CkcAPITestCase
from unittest.mock import patch, Mock


class TestCompanyUtils(CkcAPITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")

    @patch('companies.utils.Client')
    def test_assign_default_twilio_number_for_admin(self, MockClient):
        mock_request = Mock()
        mock_request.user.email = 'samote.wood@test.com'
        mock_request.user.is_superuser = True

        assign_company_assistant_number(mock_request, self.company)

        self.assertEqual(self.company.assistant_phone_number, DEFAULT_TWILIO_NUMBER)

    @patch('companies.utils.Client')
    def test_assign_available_toll_free_number(self, MockClient):
        mock_request = Mock()
        mock_request.user.email = 'nonadmin@test.com'
        mock_request.user.is_superuser = False

        MockClient.return_value.incoming_phone_numbers.list.return_value = [
            Mock(phone_number='+18001234567'),
            Mock(phone_number='+18001234568')
        ]

        assign_company_assistant_number(mock_request, self.company)

        self.assertEqual(self.company.assistant_phone_number, '+18001234567')

    @patch('companies.utils.Client')
    def test_purchase_new_number(self, MockClient):
        mock_request = Mock()
        mock_request.user.email = 'nonadmin@test.com'
        mock_request.user.is_superuser = False

        MockClient.return_value.incoming_phone_numbers.list.return_value = []
        MockClient.return_value.available_phone_numbers.return_value.toll_free.list.return_value = [
            Mock(phone_number='+18001234569')
        ]

        assign_company_assistant_number(mock_request, self.company)

        self.assertEqual(self.company.assistant_phone_number, '+18001234569')

    # Add more tests as needed.


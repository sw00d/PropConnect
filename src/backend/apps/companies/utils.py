import logging

from twilio.rest import Client

from companies.models import Company
from conversations.models import PhoneNumber
from conversations.tasks import purchase_phone_number_util
from conversations.utils import send_message
from settings.base import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, DEFAULT_TWILIO_NUMBER

twilio_auth_token = TWILIO_AUTH_TOKEN
twilio_sid = TWILIO_ACCOUNT_SID

logger = logging.getLogger(__name__)


def assign_company_assistant_number(request, company: Company):
    client = Client(twilio_sid, twilio_auth_token)
    number_to_purchase = client.available_phone_numbers("US").toll_free.list(limit=3)[0]
    # Fetch all purchased phone numbers
    numbers = client.incoming_phone_numbers.list(limit=100)
    # TODO once we get more than 100 toll free numbers, we'll have to revise this I think`

    # Filter for toll-free numbers (assuming they start with '+18' for North America)
    toll_free_numbers = [number.phone_number for number in numbers if number.phone_number.startswith('+18')]
    available_toll_free_number = None

    for toll_free_number in toll_free_numbers:
        if not Company.objects.filter(assistant_phone_number=toll_free_number):
            available_toll_free_number = toll_free_number
            break

    if 'samote.wood' in request.user.email or request.user.is_superuser:
        logger.info(f"Using admin number: {DEFAULT_TWILIO_NUMBER}")
        print(f"Using admin number: {DEFAULT_TWILIO_NUMBER}")
        company.assistant_phone_number = DEFAULT_TWILIO_NUMBER
    elif available_toll_free_number:
        print(f"Using available, already purchased number: {available_toll_free_number}")
        company.assistant_phone_number = available_toll_free_number
        phone_num_obj, _ = PhoneNumber.objects.get_or_create(number=available_toll_free_number)
        phone_num_obj.is_base_number = True
        phone_num_obj.company = company
        phone_num_obj.save()
    else:
        logger.info(f"Purchasing new company number: {number_to_purchase.phone_number}")
        purchase_phone_number_util(number_to_purchase.phone_number, "/init_conversation/", 'toll-free')
        company.assistant_phone_number = number_to_purchase.phone_number
        PhoneNumber.objects.create(number=number_to_purchase.phone_number, is_base_number=True, company=company)

    company.save()

    # Just alerting Sam that a new conversation has started, and he should probably go look at it
    send_message('+12086608828', DEFAULT_TWILIO_NUMBER,
                 f"New company signed up {company.name} with phone number {company.assistant_phone_number}")

import logging

from twilio.rest import Client

from companies.models import Company
from conversations.models import PhoneNumber
from conversations.tasks import purchase_phone_number_util
from conversations.utils import send_message
from django.conf import settings

TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
DEFAULT_TWILIO_NUMBER = settings.DEFAULT_TWILIO_NUMBER

twilio_auth_token = TWILIO_AUTH_TOKEN
twilio_sid = TWILIO_ACCOUNT_SID

logger = logging.getLogger(__name__)


def assign_company_assistant_number(request, company: Company):
    client = Client(twilio_sid, twilio_auth_token)
    number_to_purchase = client.available_phone_numbers("US").local.list(area_code="619")[0]  # TODO This area code should be based off company location
    # Fetch all purchased phone numbers

    try:

        # Filter for toll-free numbers (assuming they start with '+18' for North America)
        all_numbers = client.incoming_phone_numbers.list(limit=100)
        # TODO once we get more than 100  numbers, we'll have to revise this I think

        assistant_numbers_raw = []
        for number in all_numbers:
            if isinstance(number.friendly_name, str):
                if 'assistant_number' in number.friendly_name:
                    assistant_numbers_raw.append(number.phone_number)

        available_assistant_number = None

        for assistant_number in assistant_numbers_raw:
            if not Company.objects.filter(assistant_phone_number=assistant_number):
                available_assistant_number = assistant_number
                break

        if 'samote.wood' in request.user.email or request.user.is_superuser:
            logger.info(f"Using admin number: {DEFAULT_TWILIO_NUMBER}")
            print(f"Using admin number: {DEFAULT_TWILIO_NUMBER}")
            company.assistant_phone_number = DEFAULT_TWILIO_NUMBER
        elif available_assistant_number:
            logger.info(f"Using available, already purchased number: {available_assistant_number}")
            company.assistant_phone_number = available_assistant_number
            phone_num_obj, _ = PhoneNumber.objects.get_or_create(number=available_assistant_number)
            phone_num_obj.is_base_number = True
            phone_num_obj.company = company
            phone_num_obj.save()
        else:

            logger.info(f"Purchasing new company number: {number_to_purchase.phone_number}")
            purchased_number = purchase_phone_number_util(number_to_purchase.phone_number, "/init_conversation/")

            purchased_number.update(friendly_name=f'assistant_number_{company.name}')

        company.save()
    except Exception as e:
        logger.error(f"Error assigning company assistant number: {e}", extra={'notify_slack': True})

        send_message('+12086608828', DEFAULT_TWILIO_NUMBER,
                     f"Company: {company.name} with phone number {company.assistant_phone_number} failed to assign assistant number.")

    # Just alerting Sam that a new conversation has started, and he should probably go look at it
    send_message('+12086608828', DEFAULT_TWILIO_NUMBER,
                 f"New company signed up {company.name} with phone number {company.assistant_phone_number}")

    logger.error(f"New company has signed up! \n\n Name: {company.name} \n Size: {company.number_of_doors}", extra={'notify_slack': True})

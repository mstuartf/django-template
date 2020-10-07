import logging

from apps.accounts.models import Account
# from apps.notifications.models import EmailVerification
from utils.email_client import EmailClient

logger = logging.getLogger(__name__)


def queue_account_email_verification(pk, verification_link):
    account = Account.objects.get(pk=pk)

    # message = EmailVerification.objects.filter(account=account)
    # if message.exists():
    #     logger.info("verification email already sent for account {}; not re-sending".format(account.id))
    #     return

    logger.info("queuing verification email for account {}".format(account.id))
    email_client = EmailClient()

    email_client.send_email(
        account.email,
        "Verify email address: {}".format(account.email),
        "email_verification", {
            "verification_link": verification_link,
            "merchant_name": "{}".format(account.business_profile.name),
        }
    )

    # message = EmailVerification(message_id=message_id, account=account)
    # message.save()

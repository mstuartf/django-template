import logging

from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse

from utils.email_client import EmailClient

logger = logging.getLogger(__name__)


class CustomPasswordResetForm(PasswordResetForm):

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):

        logger.info("custom send_mail triggered for reset password form")
        path = reverse(
            "password_reset_confirm", kwargs={
                "uidb64": context["uid"],
                "token": context["token"],
            })

        reset_link = "{}://{}{}".format(context["protocol"], context["domain"], path)

        # this email is sent synchronously to avoid having to send tokens etc in payload to worker
        email_client = EmailClient()
        email_client.send_email(
            to_email,
            "Password reset",
            "password_reset",
            {
                "reset_link": reset_link
            }
        )


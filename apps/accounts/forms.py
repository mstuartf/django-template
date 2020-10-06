import logging

from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse

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
        logger.info("TODO: send email reset link {} to {}".format(reset_link, to_email))


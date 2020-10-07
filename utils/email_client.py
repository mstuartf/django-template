import os
import logging
import requests

logger = logging.getLogger(__name__)


class EmailClient:

    activity_address = os.environ.get("ACTIVITY_EMAIL")
    test_address = os.environ.get("TEST_EMAIL")
    from_address = os.environ.get('FROM_ADDRESS')

    mailgun_base_url = os.environ.get('MAILGUN_BASE_URL')
    mailgun_domain = os.environ.get('MAILGUN_DOMAIN')
    mailgun_api_key = os.environ.get('MAILGUN_API_KEY')

    def send_email(self, email_address, subject, template_id, template_args=None):

        template_args = template_args or {}

        to = email_address
        if email_address.startswith("test@"):
            logger.info("routing email from {} to {}".format(email_address, self.test_address))
            to = self.test_address
            subject = "{} [{}]".format(subject, email_address)

        payload = {
            'to': to,
            'subject': subject,
            'from': self.from_address,
            'template': template_id,
        }

        if to != self.test_address:
            payload['bcc'] = self.activity_address

        for k, v in template_args.items():
            payload['v:{}'.format(k)] = v

        logger.info(payload)

        request = requests.post(
            '{}/{}/messages'.format(self.mailgun_base_url, self.mailgun_domain),
            auth=('api', self.mailgun_api_key),
            data=payload
        )

        try:
            request.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(e.response)
            raise
        except Exception as e:
            logger.error(e)
            raise

        logger.info("request status: {}".format(request.status_code))

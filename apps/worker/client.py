import json
import os
import logging

from api.settings import boto3_session


logger = logging.getLogger(__name__)

# this class is the API to send deferred tasks to the worker
# it can be used by both the web tier and the worker tier


class WorkerClient:

    # uncomment when setting up worker
    sqs = boto3_session.resource("sqs", region_name="eu-west-2")
    queue = sqs.get_queue_by_name(QueueName=os.environ.get("AWS_WORKER_QUEUE"))

    def _queue_task(self, payload):
        # uncomment when setting up worker
        response = self.queue.send_message(MessageBody=json.dumps(payload))
        return response.get('MessageId')

    def queue_account_email_verification_task(self, account_id, verification_link):

        logger.info("queuing account verification link task for account {} with link {}".format(
            account_id, verification_link)
        )

        return self._queue_task({
            "WORKER_TASK": "EMAIL_VERIFICATION",
            "ACCOUNT_ID": account_id,
            "VERIFICATION_LINK": verification_link,
        })

import json
import logging
import os

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes

from .handlers import verification

logger = logging.getLogger(__name__)


# this endpoint receives all deferred tasks from the queue

@api_view(["POST"])
@permission_classes([])
def worker_task_handler(request):

    # AWS
    # The daemon process for the worker attaches a X-Aws-Sqsd-Queue header to the request.

    # Django:
    # With the exception of CONTENT_LENGTH and CONTENT_TYPE, as given above, any HTTP headers in the request are
    # converted to META keys by converting all characters to uppercase, replacing any hyphens with underscores
    # and adding an HTTP_ prefix to the name.
    queue_name = request.META.get("HTTP_X_AWS_SQSD_QUEUE")

    if queue_name != os.environ.get("AWS_WORKER_QUEUE"):
        logger.warning("request not sent by correct SQS queue; blocking")
        return HttpResponse(status=401, content="")

    body = json.loads(request.body)
    worker_task = body["WORKER_TASK"]
    logger.info("worker received trigger for task {}".format(worker_task))

    # add conditional handling for tasks here
    if worker_task == "EMAIL_VERIFICATION":
        verification.queue_account_email_verification(body["ACCOUNT_ID"], body["VERIFICATION_LINK"])

    else:
        logger.info("unrecognised task {}".format(worker_task))

    return HttpResponse(status=200)


# add endpoints for cron jobs here

# @api_view(["POST"])
# @permission_classes([])
# def example_cron_task(request):
#
#     # logic for scheduled task
#
#     return HttpResponse(status=200)

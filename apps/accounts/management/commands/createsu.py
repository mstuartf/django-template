import os

from django.core.management.base import BaseCommand

from apps.accounts.models import Account


class Command(BaseCommand):

    def handle(self, *args, **options):

        email_address = os.environ.get("ADMIN_EMAIL_ADDRESS")
        password = os.environ.get("ADMIN_PASSWORD")

        if not Account.objects.filter(email=email_address).exists():
            Account.objects.create_superuser(email_address, password)

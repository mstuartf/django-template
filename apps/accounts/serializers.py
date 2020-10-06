import random
import string
import logging

from django.urls import reverse

from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from apps.company.models import Company
from apps.company.serializers import CompanySerializer
from .models import Account

from apps.worker.client import WorkerClient


logger = logging.getLogger(__name__)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('email', 'first_name', 'last_name', 'id')


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('email', 'is_verified')


class CompanySignUpSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    company = CompanySerializer(write_only=True)

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        company_data = validated_data.pop('company')

        company = Company(**company_data)
        company.save()

        password = validated_data.pop('password', None)
        account = self.Meta.model(**validated_data)
        account.set_password(password)

        account.verification_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))
        account.company = company
        account.save()

        # the url can't be built by the worker as it is served on localhost
        verification_link = self.context["request"].build_absolute_uri(
            reverse(
                "verify_account",
                kwargs={
                    'email_address': account.email,
                    'verification_code': account.verification_code
                }
            )
        )

        worker = WorkerClient()
        worker.queue_account_email_verification_task(account.id, verification_link)

        return account

    class Meta:
        model = Account
        fields = ('token', 'email', 'password', 'company')

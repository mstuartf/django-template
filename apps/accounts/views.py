import logging

from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render

from .serializers import AccountSerializer, CompanySignUpSerializer

from apps.accounts.models import Account


@api_view(["GET"])
@permission_classes([])  # override default permission requirement
def verify_account(request, email_address=None, verification_code=None):
    account = Account.objects.get(email=email_address)

    if account.verification_code != verification_code:
        logging.error("codes do not match: {} vs. {}".format(account.verification_code, verification_code))
        raise Exception("invalid code")

    account.is_verified = True
    account.save()

    return render(request, 'accounts/verified.html')


class AccountList(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request):

        serializer = CompanySignUpSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):

        if not request.user.is_authenticated:
            return Response("NOT ALLOWED", status=status.HTTP_401_UNAUTHORIZED)

        serializer = AccountSerializer(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

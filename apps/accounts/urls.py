from django.urls import path
from . import views

from rest_framework_jwt.views import obtain_jwt_token
from .forms import CustomPasswordResetForm

from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView, PasswordResetCompleteView

urlpatterns = [
    path('', views.AccountList.as_view()),
    path('auth/', obtain_jwt_token),  # this is the login url
    path('verify/<email_address>/<verification_code>', views.verify_account, name="verify_account"),
    path('password_reset/', PasswordResetView.as_view(form_class=CustomPasswordResetForm), name='password_reset'),
    path('password_reset/confirm/<uidb64>/<token>', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/done', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/complete', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

from django.db import models
from django.contrib.auth.models import AbstractUser

from .manager import AccountManager
from apps.company.models import Company


# If you’re starting a new project, it’s highly recommended to set up a custom user model, even if the default User
# model is sufficient for you. This model behaves identically to the default user model, but you’ll be able to
# customize it in the future if the need arises.
class Account(AbstractUser):
    created_on = models.DateTimeField(auto_now_add=True)

    username = None
    email = models.EmailField(unique=True)

    verification_code = models.TextField()
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = AccountManager()

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.email

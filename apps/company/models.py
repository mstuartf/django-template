from django.db import models


class Company(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.TextField()

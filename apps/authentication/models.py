from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """This class extends the django user class."""
    canvas_auth_token = models.CharField(blank=True, null=True)
    
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    photo_url = models.URLField(blank=True, null=True)

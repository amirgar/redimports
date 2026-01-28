# telegram_auth/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    photo_url = models.URLField(blank=True, null=True)
    
    # Новые поля
    patronymic = models.CharField(max_length=150, blank=True, null=True, verbose_name="Отчество")
    firstName = models.CharField(max_length=150, blank=True, null=True, verbose_name="Имя")
    lastName = models.CharField(max_length=150, blank=True, null=True, verbose_name="Фамилия")
    gender = models.CharField(max_length=10, choices=[('male', 'Мужчина'), ('female', 'Женщина')], blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username or str(self.telegram_id)
    
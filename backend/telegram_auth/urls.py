from django.urls import path
from .views import TelegramAuthView

urlpatterns = [
    path('login/', TelegramAuthView.as_view(), name='telegram-login'),
]

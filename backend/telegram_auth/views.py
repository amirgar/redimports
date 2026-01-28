import json
import hashlib
import hmac
from urllib.parse import parse_qsl
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from telegram_auth.models import User  # твоя модель пользователя
from rest_framework_simplejwt.tokens import RefreshToken

def verify_telegram_data(init_data: str, bot_token: str) -> dict | None:
    data = dict(parse_qsl(init_data, strict_parsing=True))
    received_hash = data.pop("hash", None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash != received_hash:
        return None
    return data

class TelegramAuthView(APIView):
    def post(self, request):
        init_data = request.data.get("initData")
        if not init_data:
            return Response({"error": "initData required"}, status=status.HTTP_400_BAD_REQUEST)

        data = verify_telegram_data(init_data, settings.TELEGRAM_BOT_TOKEN)
        if not data:
            return Response({"error": "Invalid Telegram data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_data = json.loads(data["user"])
        except (KeyError, json.JSONDecodeError):
            return Response({"error": "Invalid user data"}, status=status.HTTP_400_BAD_REQUEST)

        telegram_id = user_data["id"]

        user, created = User.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": user_data.get("username"),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "photo_url": user_data.get("photo_url"),
            }
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "id": user.id,
                "telegram_id": telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "photo_url": user.photo_url,
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })


# telegram_auth/views.py (или catalog/views.py)
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User

@csrf_exempt
def save_profile_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        tg_id = data.get("telegram_id")
        
        # Находим юзера по telegram_id
        user = User.objects.filter(telegram_id=tg_id).first()
        if user:
            user.first_name = data.get("first_name", user.first_name)
            user.last_name = data.get("last_name", user.last_name)
            user.patronymic = data.get("patronymic", user.patronymic)
            user.gender = data.get("gender", user.gender)
            user.save()
            return JsonResponse({"status": "success"})
            
    return JsonResponse({"status": "error"}, status=400)

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import traceback # Для вывода полной ошибки
from django.shortcuts import get_object_or_404
from catalog.models import User, Product # Убедись, что импортировал модель Product

# --- АВТОРИЗАЦИЯ ЧЕРЕЗ СЕССИИ (Для работы шаблонов) ---
@csrf_exempt
def telegram_auth(request):
    # 1. Проверка метода
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        # 2. Читаем и выводим сырые данные (ДЛЯ ОТЛАДКИ)
        body_unicode = request.body.decode('utf-8')
        print(f"🔍 DEBUG: Raw Body: {body_unicode}")

        data = json.loads(body_unicode)
        
        # Получаем ID. Важно привести к строке или int в зависимости от твоей модели
        telegram_id = data.get('id')
        print(f"🔍 DEBUG: Parsed TG ID: {telegram_id}")

        if not telegram_id:
            print("❌ DEBUG: Error - No telegram_id in data")
            return JsonResponse({'error': 'No telegram_id'}, status=400)

        # 3. Сохранение в БД
        # Используем update_or_create, чтобы не было ошибки, если юзер уже есть
        print("🔍 DEBUG: Attempting DB save...")
        
        user, created = User.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': data.get('username', f'tg_{telegram_id}'),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                # ПРОВЕРЬ: есть ли поле photo_url в твоей модели User? 
                # Если нет — удали строчку ниже:
                'photo_url': data.get('photo_url', ''), 
            }
        )
        print(f"✅ DEBUG: DB Save Success. User ID: {user.id}, Created: {created}")

        # 4. Сохранение сессии
        request.session['telegram_id'] = telegram_id
        request.session.modified = True
        
        return JsonResponse({'status': 'ok', 'user_id': user.id})

    except Exception as e:
        # 5. Если случилась ошибка — выводим её в консоль
        print(f"❌❌❌ CRITICAL ERROR in telegram_auth:")
        print(str(e))
        traceback.print_exc() # Покажет точную строку ошибки
        return JsonResponse({'error': str(e)}, status=400)


# --- ЛОГИКА ИЗБРАННОГО ---
@csrf_exempt
def toggle_favorite(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    # Получаем telegram_id из сессии (которую мы установили в telegram_auth)
    telegram_id = request.session.get('telegram_id')
    
    # Если сессии нет (например, зашли с браузера без ТГ), пробуем достать из тела запроса (небезопасно, но для Mini App допустимо)
    # Но лучше полагаться на сессию.
    if not telegram_id:
        return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=401)

    product_id = request.POST.get('product_id')
    
    if not product_id:
        # Если отправляли JSON, а не Form Data
        try:
            body_data = json.loads(request.body)
            product_id = body_data.get('product_id')
        except:
            pass

    if not product_id:
        return JsonResponse({'status': 'error', 'message': 'No product_id'}, status=400)

    user = User.objects.filter(telegram_id=telegram_id).first()
    product = get_object_or_404(Product, id=product_id)

    if not user:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

    # Логика добавления/удаления (предполагаем ManyToMany поле favorites у User или Product)
    # Вариант 1: Если favorites в User
    if product in user.favorites.all():
        user.favorites.remove(product)
        status = 'removed'
    else:
        user.favorites.add(product)
        status = 'added'
        
    return JsonResponse({'status': status})
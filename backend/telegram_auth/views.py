import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from catalog.models import User, Product # Убедись, что импортировал модель Product

# --- АВТОРИЗАЦИЯ ЧЕРЕЗ СЕССИИ (Для работы шаблонов) ---
@csrf_exempt
def telegram_auth(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
        # JS initDataUnsafe.user возвращает объект с полем 'id' (int)
        telegram_id = data.get('id')

        if not telegram_id:
            return JsonResponse({'error': 'No telegram_id'}, status=400)

        # Создаем или обновляем пользователя
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': data.get('username', f'tg_{telegram_id}'),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'photo_url': data.get('photo_url', ''),
            }
        )
        
        # !ВАЖНО: Сохраняем ID в сессию Django
        request.session['telegram_id'] = telegram_id
        request.session.modified = True 
        
        return JsonResponse({'status': 'ok', 'user_id': user.id})
    except Exception as e:
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
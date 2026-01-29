import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from catalog.models import Product, Favorite

User = get_user_model()

@csrf_exempt
def telegram_auth(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body.decode('utf-8'))
        tg_id = data.get('id')

        if not tg_id:
            return JsonResponse({'error': 'No telegram_id'}, status=400)

        # Теперь мы ищем именно по telegram_id
        user, created = User.objects.update_or_create(
            telegram_id=tg_id,
            defaults={
                'username': data.get('username') or f"user_{tg_id}",
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'photo_url': data.get('photo_url', ''),
            }
        )
        
        # Сохраняем в сессию
        request.session['telegram_id'] = tg_id
        request.session.modified = True
        
        return JsonResponse({'status': 'ok', 'is_new': created})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def toggle_favorite(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    tg_id = request.session.get('telegram_id')
    if not tg_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    # Получаем ID товара из POST-запроса
    product_id = request.POST.get('product_id')
    
    user = get_object_or_404(User, telegram_id=tg_id)
    product = get_object_or_404(Product, id=product_id)

    # Используем твою модель Favorite
    favorite, created = Favorite.objects.get_or_create(user=user, product=product)
    
    if not created:
        favorite.delete()
        return JsonResponse({'status': 'removed'})
    
    return JsonResponse({'status': 'added'})
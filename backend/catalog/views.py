from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import render
from django.db.models import Q
from django.db.models import Min, Max


from .models import (
    Category, ProductType, Product, Brand,
    Cart, CartItem, Saved,
)
from .serializers import (
    CategorySerializer, ProductTypeSerializer,
    ProductSerializer, BrandSerializer,
    CartSerializer, SavedSerializer
)

# --------------------------
# Категории / Товары / Бренды
# --------------------------
class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(
            categories,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class ProductTypeByCategoryView(APIView):
    def get(self, request, category_id):
        types = ProductType.objects.filter(category_id=category_id)
        serializer = ProductTypeSerializer(types, many=True)
        return Response(serializer.data)


class ProductByTypeView(APIView):
    def get(self, request, type_id):
        products = Product.objects.filter(product_type_id=type_id)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailView(APIView):
    def get(self, request, product_id):
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


class BrandListView(APIView):
    def get(self, request):
        brands = Brand.objects.all()
        serializer = BrandSerializer(brands, many=True, context={'request': request})
        return Response(serializer.data)



class ProductsByBrandView(APIView):
    def get(self, request, brand_id):
        products = Product.objects.filter(brand_id=brand_id)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


# --------------------------
# Поиск / Фильтры
# --------------------------
class ProductSearchView(APIView):
    def get(self, request):
        products = Product.objects.all()

        # Поиск по имени/описанию
        query = request.GET.get('q')
        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )

        # Фильтр по бренду
        brand_id = request.GET.get('brand')
        if brand_id:
            products = products.filter(brand_id=brand_id)

        # Фильтр по категории
        category_id = request.GET.get('category')
        if category_id:
            products = products.filter(product_type__category_id=category_id)

        # Фильтр по цене
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


# --------------------------
# Saved (Избранное)
# --------------------------
class SavedListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved_items = Saved.objects.filter(user=request.user).order_by('-created_at')
        serializer = SavedSerializer(saved_items, many=True)
        return Response(serializer.data)


class SavedAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        saved, created = Saved.objects.get_or_create(user=request.user, product=product)
        return Response({'added': created})


class SavedRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        try:
            saved = Saved.objects.get(user=request.user, product_id=product_id)
            saved.delete()
            return Response({'removed': True})
        except Saved.DoesNotExist:
            return Response({'removed': False})


# --------------------------
# Cart (Корзина)
# --------------------------
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = Product.objects.get(id=product_id)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += 1
            item.save()

        return Response({"added": True})


class CartRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        return Response({"deleted": True})


class CartUpdateQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        quantity = int(request.data.get("quantity", 1))
        cart, _ = Cart.objects.get_or_create(user=request.user)

        try:
            item = CartItem.objects.get(cart=cart, product_id=product_id)
            item.quantity = max(1, quantity)
            item.save()
            return Response({"updated": True})
        except CartItem.DoesNotExist:
            return Response({"error": "Item not in cart"}, status=status.HTTP_404_NOT_FOUND)


# --------------------------
# Order (Создание заказа)
# --------------------------
class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user)

        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        data = request.data
        required_fields = ['first_name', 'last_name', 'phone', 'address', 'delivery_type', 'payment_method']
        for field in required_fields:
            if field not in data:
                return Response({"error": f"{field} is required"}, status=400)

        order = Order.objects.create(
            user=user,
            first_name=data['first_name'],
            last_name=data['last_name'],
            middle_name=data.get('middle_name', ''),
            phone=data['phone'],
            address=data['address'],
            delivery_type=data['delivery_type'],
            payment_method=data['payment_method'],
            total_price=cart.total_price()
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.discount_price or item.product.price,
                quantity=item.quantity
            )

        cart.items.all().delete()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=201)

from django.views.generic import TemplateView
from .models import HeroBlock
from .models import Category

def home(request):
    categories = Category.objects.all()[:2]
    categories_count = Category.objects.count()

    brands = Brand.objects.all()
    brands_count = Brand.objects.count()  # опционально
    new_products = Product.objects.filter(is_new=True).prefetch_related('images').all()
    new_products_counter = Product.objects.filter(is_new=True).count()
    all_products = Product.objects.prefetch_related('images').all()
    all_products_counter = Product.objects.count()
    recommended_products = Product.objects.all().prefetch_related('images')[:4]
    hero = HeroBlock.objects.filter(is_active=True).first()

    return render(request, 'catalog/home.html', {
        'categories': categories,
        'categories_count': categories_count,
        'brands': brands,
        'brands_count': brands_count,  # если понадобится
        'new_products': new_products,
        'new_products_counter': new_products_counter,
        'recommended_products': recommended_products,
        'all_products': all_products,
        'all_products_counter': all_products_counter,
        'hero': hero,
    })

def catalog(request):
    categories = Category.objects.all()
    return render(request, 'catalog/catalog.html', {
        'categories': categories
    })

def search_results(request):
    query = request.GET.get('q', '').strip()

    products = Product.objects.prefetch_related('images', 'brand')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__name__icontains=query)
        )

    return render(request, 'catalog/search-results.html', {
        'all_products': products,
        'all_products_counter': products.count(),
        'query': query,
    })

from django.shortcuts import get_object_or_404
from telegram_auth.models import User


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'brand'),
        pk=pk
    )
    telegram_id = request.session.get('telegram_id')
    favorite_products = []
    user = None
    if telegram_id:
        user = User.objects.filter(telegram_id=telegram_id).first()
        if user:
            favorite_products = Product.objects.filter(
                favorited_by__user=user
            )

    params = product.parameter_list or {}
    sizes = params.get('sizes', [])
    attributes = {
        key: value
        for key, value in params.items()
        if key != 'sizes'
    }

    # products_count = product.count()
    context = {
        'product': product,
        'sizes': sizes,
        'attributes': attributes,
        'favoutite_products': favorite_products,
    }

    return render(request, 'catalog/product-card.html', context)


def product_card(request): 
    new_products = Product.objects.filter(is_new=True).prefetch_related('images', 'brand')
    all_products = Product.objects.prefetch_related('images', 'brand')


    context = {
        'new_products': new_products,
        'new_products_counter': new_products.count(),

        'all_products': all_products,
        'all_products_counter': all_products.count(),

        'brands': Brand.objects.all(),
        'brands_count': Brand.objects.count(),
    }

    return render(request, 'catalog/product-card.html', context)

# views.py
from django.shortcuts import render, get_object_or_404
from .models import Category, Product

from django.shortcuts import get_object_or_404, render
from .models import Product, Category

from django.shortcuts import get_object_or_404, render
from .models import Category, Product

def category_details(request, pk):
    category = get_object_or_404(ProductType, id=pk)
    
    # 1. Фильтруем то, что SQLite умеет делать (Бренды, Цены, Скидки)
    products_qs = Product.objects.filter(product_type=category).prefetch_related('images', 'brand')

    if request.GET.get('discount'):
        products_qs = products_qs.filter(discount_price__isnull=False)

    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        products_qs = products_qs.filter(brand_id__in=selected_brands)

    p_from = request.GET.get('price_from') or request.GET.get('min_price')
    p_to = request.GET.get('price_to') or request.GET.get('max_price')
    if p_from: products_qs = products_qs.filter(price__gte=p_from)
    if p_to: products_qs = products_qs.filter(price__lte=p_to)

    # 2. Фильтруем JSON-параметры вручную (для совместимости с SQLite)
    exclude_keys = ['brand', 'discount', 'price_from', 'price_to', 'min_price', 'max_price', 'v', 'q']
    
    # Собираем только те фильтры, которые есть в URL и не являются системными
    active_json_filters = {
        k: v for k, v in request.GET.lists() 
        if k not in exclude_keys and v
    }

    if active_json_filters:
        filtered_ids = []
        # Проходим по товарам и проверяем соответствие JSON
        for product in products_qs:
            params = product.parameter_list or {}
            is_match = True
            
            for key, values in active_json_filters.items():
                val_in_db = params.get(key)
                
                if isinstance(val_in_db, list):
                    # Если в базе список (например, sizes: ["40", "42"]), ищем пересечение
                    if not any(str(v) in map(str, val_in_db) for v in values):
                        is_match = False
                        break
                else:
                    # Если в базе одиночное значение, проверяем вхождение
                    if str(val_in_db) not in values:
                        is_match = False
                        break
            
            if is_match:
                filtered_ids.append(product.id)
        
        # Оставляем только те товары, которые прошли проверку
        products = Product.objects.filter(id__in=filtered_ids).prefetch_related('images', 'brand')
    else:
        products = products_qs

    # 3. Данные для фильтров
    brands = Brand.objects.filter(products__product_type=category).distinct()
    price_stats = Product.objects.filter(product_type=category).aggregate(
        min_p=Min('price'), max_p=Max('price')
    )

    context = {
        'category': category,
        'products': products.distinct(),
        'brands': brands,
        'selected_brands': selected_brands,
        'min_price': price_stats['min_p'] or 0,
        'max_price': price_stats['max_p'] or 0,
    }

    return render(request, 'catalog/category.html', context)

from collections import defaultdict

from collections import defaultdict
from django.shortcuts import render, get_object_or_404
from django.db.models import Min, Max
from .models import Product, ProductType, Brand



def filters_view(request, category_id):
    """Страница выбора фильтров"""
    category = get_object_or_404(ProductType, id=category_id)
    
    # Берем ВСЕ товары категории для построения полного списка опций
    base_qs = Product.objects.filter(product_type=category)
    
    # Сбор всех возможных вариантов (размеры, цвета и т.д.)
    filters_data = defaultdict(set)
    sizes_set = set()

    for product in base_qs:
        params = product.parameter_list or {}
        for k, v in params.items():
            if k == 'sizes' and isinstance(v, list):
                sizes_set.update(map(str, v))
            elif isinstance(v, list):
                filters_data[k].update(map(str, v))
            else:
                filters_data[k].add(str(v))

    # Красивая сортировка размеров (числа как числа)
    sorted_sizes = sorted(
        list(sizes_set), 
        key=lambda x: int(x) if x.isdigit() else x
    )

    # Статистика цен для плейсхолдеров
    price_stats = base_qs.aggregate(min_p=Min('price'), max_p=Max('price'))
    min_p_val = price_stats['min_p'] or 0
    max_p_val = price_stats['max_p'] or 0

    context = {
        "category": category,
        "filters": {k: sorted(list(v)) for k, v in filters_data.items()},
        "sizes": sorted_sizes,
        "brands": Brand.objects.filter(products__in=base_qs).distinct(),
        
        # Передаем текущие выбранные параметры, чтобы JS мог их подсветить
        "selected_brands": request.GET.getlist('brand'),
        "min_price": price_stats['min_p'] or 0,
        "max_price": price_stats['max_p'] or 0,
    }

    return render(request, "catalog/filter.html", context)


def profile(request): 
    return render(request, 'catalog/profile.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram_auth.models import User
from catalog.models import Product, Favorite

@csrf_exempt
def toggle_favorite(request):
    telegram_id = request.session.get('telegram_id')

    if not telegram_id:
        return JsonResponse({'error': 'unauthorized'}, status=401)

    user = User.objects.filter(telegram_id=telegram_id).first()
    if not user:
        return JsonResponse({'error': 'user not found'}, status=404)

    product_id = request.POST.get('product_id')
    product = Product.objects.get(id=product_id)

    favorite = Favorite.objects.filter(user=user, product=product)

    if favorite.exists():
        favorite.delete()
        return JsonResponse({'status': 'removed'})
    else:
        Favorite.objects.create(user=user, product=product)
        return JsonResponse({'status': 'added'})

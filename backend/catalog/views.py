from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import render
from django.db.models import Q

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

def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'brand'),
        pk=pk
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

def category_details(request, pk):
    category = get_object_or_404(Category, pk=pk)

    products = Product.objects.filter(
        product_type_id=category.id
    ).select_related('brand').prefetch_related('images')

    return render(request, 'catalog/category.html', {
        'category': category,
        'products': products,
    })

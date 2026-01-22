# orders/views.py
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Order
from .serializers import OrderListSerializer, OrderDetailSerializer


class OrderListView(ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Order, OrderItem
from .serializers import CreateOrderSerializer
from catalog.models import Cart


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        # 1️⃣ Получаем корзину
        try:
            cart = user.cart
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not cart.items.exists():
            return Response(
                {'error': 'Корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2️⃣ Создаём заказ
        order = Order.objects.create(
            user=user,
            total_price=cart.total_price(),
            **serializer.validated_data
        )

        # 3️⃣ Переносим товары из корзины в заказ
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )

        # 4️⃣ Очищаем корзину
        cart.items.all().delete()

        return Response(
            {
                'order_id': order.id,
                'total_price': order.total_price
            },
            status=status.HTTP_201_CREATED
        )

from .models import Payment


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {'error': 'Заказ не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        if hasattr(order, 'payment'):
            return Response(
                {'error': 'Платёж уже создан'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = Payment.objects.create(
            order=order,
            provider=serializer.validated_data['provider'],
            amount=order.total_price
        )

        return Response(
            {
                'payment_id': payment.id,
                'amount': payment.amount,
                'status': payment.status
            },
            status=status.HTTP_201_CREATED
        )

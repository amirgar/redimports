# orders/serializers.py
from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()

class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'total_price',
            'created_at',
        ]

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'total_price',
            'created_at',

            'first_name',
            'last_name',
            'middle_name',
            'phone',
            'address',

            'delivery_method',
            'payment_method',

            'items',
        ]

from rest_framework import serializers
from .models import Order


class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'first_name',
            'last_name',
            'middle_name',
            'phone',
            'address',
            'delivery_method',
            'payment_method',
        ]

from .models import Payment


class CreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['provider']

# orders/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]

    DELIVERY_CHOICES = [
        ('pickup', 'Самовывоз'),
        ('point', 'Пункт выдачи'),
    ]

    PAYMENT_CHOICES = [
        ('card', 'Банковская карта'),
        ('yandex_split', 'Яндекс Сплит'),
        ('sbp', 'СБП'),
        ('online', 'Онлайн оплата'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)

    phone = models.CharField(max_length=20)
    address = models.TextField()

    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    total_price = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)

    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.price * self.quantity

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('failed', 'Ошибка'),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    provider = models.CharField(
        max_length=50,
        help_text='card / yandex_split / sbp'
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending'
    )

    amount = models.PositiveIntegerField()

    external_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='ID платежа в платёжной системе'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment #{self.id} for Order #{self.order.id}'

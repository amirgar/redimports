from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name


class ProductType(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='types'
    )
    name = models.CharField(max_length=255)
    parameter_list = models.JSONField()

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255)
    logo = models.FileField(upload_to='brands/')

    def __str__(self):
        return self.name


class Product(models.Model):
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE,
        related_name='products'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    parameter_list = models.JSONField()
    price = models.IntegerField()
    discount_price = models.IntegerField(null=True, blank=True)
    is_new = models.BooleanField(
        default=False,
        verbose_name='Новинка'
    )
    def __str__(self):
        return self.name

class ProductPhoto(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    def __str__(self):
        return f'{self.product.name}'

from django.db import models
from django.conf import settings

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Cart of {self.user}"

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def total_price(self):
        price = self.product.discount_price or self.product.price
        return price * self.quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"

from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Saved(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_items'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='saved_by_users'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} saved {self.product.name}"


from django.db import models


class HeroBlock(models.Model):
    image = models.ImageField(
        upload_to='hero/',
        verbose_name='Изображение'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Большой текст'
    )
    subtitle = models.TextField(
        verbose_name='Малый текст'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активный'
    )

    class Meta:
        verbose_name = 'Титульник'
        verbose_name_plural = 'Титульники'

    def __str__(self):
        return self.title

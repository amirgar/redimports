from django.contrib import admin

# Register your models here.
from orders.models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'price', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Поля, которые будут видны в таблице списка заказов
    list_display = ('id', 'user', 'first_name', 'phone', 'total_price', 'created_at', 'status')
    
    # Исправляем здесь: используем имя из твоей модели (delivery_method)
    list_filter = ('delivery_method', 'status', 'created_at') 
    
    search_fields = ('last_name', 'phone', 'user__username')
    inlines = [OrderItemInline]
from django.contrib import admin
from .models import Category, ProductType, Brand, Product, ProductPhoto, HeroBlock

# Регистрируем только модели каталога
admin.site.register(Category)
admin.site.register(ProductType)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductPhoto)

@admin.register(HeroBlock)
class HeroBlockAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    list_filter = ('is_active',)

from .models import SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('promo_text', 'is_active')
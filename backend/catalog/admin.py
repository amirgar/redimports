from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(ProductType)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductPhoto)

from django.contrib import admin
from .models import HeroBlock


@admin.register(HeroBlock)
class HeroBlockAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    list_filter = ('is_active',)

from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(ProductType)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductPhoto)
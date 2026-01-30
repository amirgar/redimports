from django.contrib import admin
from django.urls import path, include
from catalog.views import (
    home, catalog, search_results, product_card, product_detail, 
    category_details, filters_view, profile, 
    toggle_favorite, favorites_list, cart_detail, update_cart, remove_from_cart,  add_to_cart
)
from telegram_auth.views import telegram_auth
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Исправляем путь API авторизации (чтобы совпадало с JS)
    path('api/telegram/auth/', telegram_auth, name='telegram_auth'), 
    
    # Добавляем путь для избранного (которого не хватало)
    path('favorite/toggle/', toggle_favorite, name='toggle_favorite'),
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/<str:action>/', update_cart, name='update_cart'),
    path('catalog/', catalog, name='catalog'),
    path('search/', search_results, name='search'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('product/', product_card, name='product'),
    path("category/<int:category_id>/filters/", filters_view, name="filter"),
    path('category/<int:pk>/', category_details, name='category_detail'),
    path('favorites/', favorites_list, name='favorites_list'),
    path('favorite/toggle/', toggle_favorite, name='toggle_favorite'),
    path('profile/', profile, name='profile'),
    path('orders/', profile, name='orders'),
    path('', home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
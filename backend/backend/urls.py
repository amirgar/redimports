from django.contrib import admin
from django.urls import path, include
from catalog.views import home, catalog, search_results, product_card, product_detail, category_details, filters_view, profile
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/catalog/', include('catalog.urls')),        # API для товаров, Cart, Saved, Order
    path('api/auth/telegram/', include('telegram_auth.urls')),  # Telegram авторизация
    path('catalog/', catalog, name='catalog'),
    path('search/', search_results, name='search'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('product/', product_card, name='product'),
    path("category/<int:category_id>/filters/", filters_view, name="filter"),
    path('category/<int:pk>/', category_details, name='category_detail'),
    path("api/telegram/", include("telegram_auth.urls")),
    path('profile/', profile, name='profile'),
    path('', home, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
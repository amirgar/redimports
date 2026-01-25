from django.contrib import admin
from django.urls import path, include
from catalog.views import home, catalog,search_results
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/catalog/', include('catalog.urls')),        # API для товаров, Cart, Saved, Order
    path('api/auth/telegram/', include('telegram_auth.urls')),  # Telegram авторизация
    path('', home, name='home'),
    path('catalog/', catalog, name='catalog'),
    path('search/', search_results, name='search'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.urls import path
from .views import (
    CategoryListView, ProductTypeByCategoryView, ProductByTypeView, ProductDetailView,
    BrandListView, ProductsByBrandView, ProductSearchView,
    SavedListView, SavedAddView, SavedRemoveView,
    CartView, CartAddView, CartRemoveView, CartUpdateQuantityView,
    OrderCreateView
)
from .views import toggle_favorite


urlpatterns = [
    # -------------------- Категории / Товары / Бренды --------------------
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:category_id>/types/', ProductTypeByCategoryView.as_view(), name='producttype-by-category'),
    path('types/<int:type_id>/products/', ProductByTypeView.as_view(), name='products-by-type'),
    path('products/<int:product_id>/', ProductDetailView.as_view(), name='product-detail'),

    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('brands/<int:brand_id>/products/', ProductsByBrandView.as_view(), name='products-by-brand'),

    # -------------------- Поиск и фильтры --------------------
    path('products/search/', ProductSearchView.as_view(), name='product-search'),

    # -------------------- Saved / Избранное --------------------
    path('saved/', SavedListView.as_view(), name='saved-list'),
    path('saved/add/', SavedAddView.as_view(), name='saved-add'),
    path('saved/remove/<int:product_id>/', SavedRemoveView.as_view(), name='saved-remove'),

    # -------------------- Cart / Корзина --------------------
    path('cart/', CartView.as_view(), name='cart-detail'),
    path('cart/add/<int:product_id>/', CartAddView.as_view(), name='cart-add'),
    path('cart/remove/<int:product_id>/', CartRemoveView.as_view(), name='cart-remove'),
    path('cart/update/<int:product_id>/', CartUpdateQuantityView.as_view(), name='cart-update'),

    # -------------------- Order / Заказы --------------------
    path('order/create/', OrderCreateView.as_view(), name='order-create'),
]

from django.urls import path
from .views import home, catalog

urlpatterns += [
    path('', home, name='home'),
    path('favorite/toggle/', toggle_favorite, name='toggle_favorite'),

    # path('catalog/', catalog, name='catalog'),
]

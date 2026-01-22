# orders/urls.py
from django.urls import path
from .views import OrderListView, OrderDetailView, CreatePaymentView

urlpatterns = [
    path('', OrderListView.as_view()),
    path('<int:pk>/', OrderDetailView.as_view()),
]

from django.urls import path
from .views import CreateOrderView

urlpatterns += [
    path('create/', CreateOrderView.as_view()),
    path('<int:order_id>/payment/', CreatePaymentView.as_view()),
]

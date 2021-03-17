from django.urls import include, path
from .views import CouriersCreateView, CouriersListView, OrdersCreateView, OrdersListView, CourierUpdateView, \
    orders_assign, order_complete
from django.conf.urls import handler400, url

urlpatterns = [
    path('couriers', CouriersCreateView.as_view()),
    path('couriersList', CouriersListView.as_view()),
    path('orders', OrdersCreateView.as_view()),
    path('ordersList', OrdersListView.as_view()),
    path('couriers/<int:pk>', CourierUpdateView.as_view()),
    path('orders/assign', orders_assign),
    path('orders/complete', order_complete)
]

# handler400 = bad_request

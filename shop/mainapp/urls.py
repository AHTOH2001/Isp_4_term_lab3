from django.urls import include, path
# from .views import CouriersCreateView, CouriersListView, OrdersCreateView, OrdersListView, CourierRetrieveUpdateView, \
#     orders_assign, order_complete, OrdersRawListView, register, register_complete, authorize, home
from . import views

# from django.conf.urls import handler400, url

urlpatterns = [
    path('couriers', views.RestAPI.CouriersCreateView.as_view()),
    # path('couriersList', CouriersListView.as_view()),
    path('orders', views.RestAPI.OrdersCreateView.as_view()),
    # path('ordersList', OrdersListView.as_view()),
    # path('ordersRawList', OrdersRawListView.as_view()),
    path('couriers/<int:pk>', views.RestAPI.CourierRetrieveUpdateView.as_view()),
    path('orders/assign', views.RestAPI.orders_assign),
    path('orders/complete', views.RestAPI.order_complete),
]

urlpatterns += [
    path('register/', views.frontend.register, name='register'),
    path('register/complete/', views.frontend.register_complete, name='register_complete'),
    path('authorize/', views.frontend.authorize, name='authorize'),
    path('', views.frontend.home, name='home'),
    path('profile/', views.frontend.profile, name='profile'),
    path('profile/create/', views.frontend.profile_create, name='profile_create'),
    path('useful-information/', views.frontend.useful_information, name='useful_information'),
    path('about-us/', views.frontend.about_us, name='about_us'),
    path('contact/', views.frontend.contact, name='contact'),
    path('logout/', views.frontend.client_logout, name='logout'),
    path('profile/edit/', views.frontend.edit, name='edit'),
    path('order/create', views.frontend.create_order, name='create_order'),
]

from django.urls import include, path
from .views import *

urlpatterns = [
    path('couriers', CouriersCreateView.as_view()),
    path('couriersList', CouriersListView.as_view()),
]

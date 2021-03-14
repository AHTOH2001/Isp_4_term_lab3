from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.views.defaults import ERROR_400_TEMPLATE_NAME
from rest_framework import generics, status
from rest_framework.decorators import api_view

from rest_framework.response import Response
from .serializers import CouriersListSerializer, CouriersCreateSerializer, OrdersListSerializer, OrdersCreateSerializer, \
    CourierSerializer
from .models import Courier, Order


class CouriersCreateView(generics.CreateAPIView):
    serializer_class = CouriersCreateSerializer

    def post(self, request, *args, **kwargs):
        result = super().post(request, *args, **kwargs)
        content = {'couriers': [{'id': courier['courier_id']} for courier in result.data['data']]}
        return Response(content, status=result.status_code)


class CouriersListView(generics.ListAPIView):
    serializer_class = CouriersListSerializer
    queryset = Courier.objects.all()


class OrdersCreateView(generics.CreateAPIView):
    serializer_class = OrdersCreateSerializer

    def post(self, request, *args, **kwargs):
        result = super().post(request, *args, **kwargs)
        content = {'orders': [{'id': order['order_id']} for order in result.data['data']]}
        return Response(content, status=result.status_code)


class OrdersListView(generics.ListAPIView):
    serializer_class = OrdersListSerializer
    queryset = Order.objects.all()


class CourierPatchView(generics.RetrieveUpdateAPIView):
    serializer_class = CourierSerializer
    queryset = Courier.objects.all()

    # def patch(self, request, *args, **kwargs):
    #     # result = super().patch(request, *args, **kwargs)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     raise Exception(serializer.__repr__())
    #     content = {'orders': [{'id': order['order_id']} for order in result.data['data']]}
    #     return Response(content, status=result.status_code)

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CouriersListSerializer, CouriersCreateSerializer, OrdersListSerializer, OrdersCreateSerializer, \
    CourierUpdateSerializer, OrdersAssignSerializer, OrderCompleteSerializer
from .models import Courier, Order
from datetime import datetime
from django.utils import timezone
from .utils import valid_orders_for_courier


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
    queryset = Order.objects.filter(is_done=False).order_by('weight')


class OrdersRawListView(generics.ListAPIView):
    serializer_class = OrdersListSerializer
    queryset = Order.objects.all()


class CourierRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = CourierUpdateSerializer
    queryset = Courier.objects.all()

    def patch(self, request, *args, **kwargs):
        courier = self.get_object()
        serializer = self.get_serializer(courier, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        taken_orders = Order.objects.filter(taken_by=courier.courier_id, is_done=False)
        valid_orders = valid_orders_for_courier(courier, taken_orders)

        for order in taken_orders:
            if order not in valid_orders:
                Order.objects.filter(order_id=order.order_id).update(taken_by=None)

        if getattr(courier, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            courier._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        courier = self.get_object()
        res = {"courier_id": courier.courier_id, "courier_type": courier.courier_type, "regions": courier.regions,
               "working_hours": courier.working_hours}

        if courier.time_regions is not None:
            res['rating'] = round((60 * 60 - min(min(courier.time_regions.values()), 60 * 60)) / (60 * 60) * 5, 2)

        res['earning'] = courier.earning

        return Response(res, status=status.HTTP_200_OK)


@api_view(['POST'])
def orders_assign(request):
    if request.method == 'POST':
        serializer = OrdersAssignSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            courier = Courier.objects.get(courier_id=request.data['courier_id'])
        except Courier.DoesNotExist:
            return Response({'courier_id': [f'Courier with id {request.data["courier_id"]} does not exist']},
                            status=status.HTTP_400_BAD_REQUEST)

        Order.objects.filter(taken_by=courier.courier_id).update(taken_by=None)
        valid_orders = valid_orders_for_courier(courier, Order.objects.filter(is_done=False, taken_by=None))

        if len(valid_orders) == 0:
            return Response({'orders': []}, status=status.HTTP_200_OK)
        else:
            if courier.assign_time is None:
                assign_time = timezone.now()
            else:
                assign_time = courier.assign_time

            Courier.objects.filter(courier_id=courier.courier_id).update(
                earning_coef=Courier.TYPE_TO_COEF[courier.courier_type], assign_time=assign_time)
            for order in valid_orders:
                Order.objects.filter(order_id=order.order_id).update(taken_by=courier.courier_id)
            return Response({'orders': [{'id': order.order_id} for order in valid_orders], 'assign_time': assign_time},
                            status=status.HTTP_200_OK)


@api_view(['POST'])
def order_complete(request):
    if request.method == 'POST':
        serializer = OrderCompleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            courier = Courier.objects.get(courier_id=request.data['courier_id'])
            order = Order.objects.get(order_id=request.data['order_id'])
        except Courier.DoesNotExist:
            return Response({'courier_id': [f'Courier with id {request.data["courier_id"]} does not exist']},
                            status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'order_id': [f'Order with id {request.data["order_id"]} does not exist']},
                            status=status.HTTP_400_BAD_REQUEST)

        if order.taken_by != courier:
            return Response({'order_id': [
                f'Order with id {request.data["order_id"]} does not taken by courier with id {request.data["courier_id"]}']},
                status=status.HTTP_400_BAD_REQUEST)

        if order.is_done:
            return Response({'order_id': [
                f'Order with id {request.data["order_id"]} is done already']},
                status=status.HTTP_400_BAD_REQUEST)

        if courier.time_regions is None:
            courier.time_regions = dict()
            courier.finished_amount_regions = dict()

        if courier.complete_time is None:
            prev_time = courier.assign_time
        else:
            prev_time = courier.complete_time

        complete_time = datetime.strptime(request.data['complete_time'], '%Y-%m-%dT%H:%M:%S.%fZ').astimezone(
            timezone.get_current_timezone())

        new_time_delta_seconds = int((complete_time - prev_time).total_seconds())
        region = str(order.region)  # cause in db key is str
        if region not in courier.time_regions:
            courier.time_regions[region] = float(0)
            courier.finished_amount_regions[region] = 0

        courier.time_regions[region] = (courier.time_regions[region] * courier.finished_amount_regions[
            region] + new_time_delta_seconds) / (courier.finished_amount_regions[region] + 1)
        courier.finished_amount_regions[region] += 1

        courier.complete_time = complete_time
        courier.total_earning += 500 * courier.earning_coef

        courier.save()
        Order.objects.filter(order_id=order.order_id).update(is_done=True)

        return Response({"order_id": order.order_id}, status=status.HTTP_200_OK)

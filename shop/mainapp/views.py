from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CouriersListSerializer, CouriersCreateSerializer, OrdersListSerializer, OrdersCreateSerializer, \
    CourierUpdateSerializer, OrdersAssignSerializer, OrderCompleteSerializer
from .models import Courier, Order
from datetime import datetime
import decimal
from django.utils import timezone
from .utils import valid_order_for_courier


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
    queryset = Order.objects.all().order_by('weight')


class CourierRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = CourierUpdateSerializer
    queryset = Courier.objects.all()

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_instance = serializer.save()
        taken_orders = Order.objects.filter(taken_by=instance.courier_id, is_done=False)
        for order in taken_orders:
            if not valid_order_for_courier(instance, order):
                Order.objects.filter(order_id=order.order_id).update(taken_by=None)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        courier = self.get_object()
        res = {"courier_id": courier.courier_id, "courier_type": courier.courier_type, "regions": courier.regions,
               "working_hours": courier.working_hours}

        if courier.time_regions is not None:
            res['rating'] = round((60 * 60 - min(min(courier.time_regions.values()), 60 * 60)) / (60 * 60) * 5, 2)

        res['total_earning'] = courier.total_earning

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

        courier_weight = decimal.Decimal(courier.TYPE_TO_VALUE[courier.courier_type])
        orders = Order.objects.filter(is_done=False).order_by('weight')
        res_orders = []
        before_taken_amount = 0
        collected_weight = decimal.Decimal('0')

        for order in orders:
            if order.taken_by == courier:
                before_taken_amount += 1
                order.taken_by = None
                Order.objects.filter(order_id=order.order_id).update(taken_by=None)

            if valid_order_for_courier(courier, order):
            if order.taken_by is None:
                if order.weight <= courier_weight - collected_weight:
                    if order.region in courier.regions:
                        order_time_ranges = [
                            ((datetime.strptime(str_time[:5], '%H:%M')), (datetime.strptime(str_time[6:], '%H:%M'))) for
                            str_time in order.delivery_hours]
                        courier_time_ranges = [
                            ((datetime.strptime(str_time[:5], '%H:%M')), (datetime.strptime(str_time[6:], '%H:%M'))) for
                            str_time in courier.working_hours]
                        success = False
                        for order_time_l, order_time_r in order_time_ranges:
                            for courier_time_l, courier_time_r in courier_time_ranges:
                                if order_time_l <= courier_time_l <= order_time_r or order_time_l <= courier_time_r <= order_time_r:
                                    success = True
                        if success:
                            collected_weight = collected_weight + order.weight
                            res_orders.append({'id': order.order_id})

        if before_taken_amount == 0 and courier.assign_time is None:
            assign_time = timezone.now()
        else:
            assign_time = courier.assign_time

        Courier.objects.filter(courier_id=courier.courier_id).update(
            earning_coef=Courier.TYPE_TO_COEF[courier.courier_type])

        if len(res_orders) == 0:
            return Response({'orders': res_orders}, status=status.HTTP_200_OK)
        else:
            Courier.objects.filter(courier_id=courier.courier_id).update(assign_time=assign_time)
            for order in res_orders:
                Order.objects.filter(order_id=order['id']).update(taken_by=courier.courier_id)
            return Response({'orders': res_orders, 'assign_time': assign_time}, status=status.HTTP_200_OK)


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

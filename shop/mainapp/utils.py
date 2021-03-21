import decimal

from rest_framework.views import exception_handler
from datetime import datetime


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == 400:
            if 'data' in response.data:
                validated_data = response.data
                if context['request'].get_full_path() == '/couriers':
                    response.data = {'validation_error': {'couriers': []}}
                    for validated, raw in zip(validated_data['data'], context['request'].data['data']):
                        if len(validated) != 0:
                            response.data['validation_error']['couriers'].append({'id': raw['courier_id']})
                elif context['request'].get_full_path() == '/orders':
                    response.data = {'validation_error': {'orders': []}}
                    for validated, raw in zip(validated_data['data'], context['request'].data['data']):
                        if len(validated) != 0:
                            response.data['validation_error']['orders'].append({'id': raw['order_id']})

    return response


def valid_orders_for_courier(courier, orders):
    courier_weight = decimal.Decimal(courier.TYPE_TO_VALUE[courier.courier_type])
    orders = sorted(orders, key=lambda x: x.weight)
    res_orders = []
    collected_weight = decimal.Decimal('0')

    for order in orders:
        result = False

        if (order.taken_by is None or order.taken_by == courier) and order.is_done is False:
            if order.region in courier.regions:
                if order.weight <= courier_weight - collected_weight:
                    order_time_ranges = [
                        ((datetime.strptime(str_time[:5], '%H:%M')), (datetime.strptime(str_time[6:], '%H:%M'))) for
                        str_time in order.delivery_hours]
                    courier_time_ranges = [
                        ((datetime.strptime(str_time[:5], '%H:%M')), (datetime.strptime(str_time[6:], '%H:%M'))) for
                        str_time in courier.working_hours]
                    for order_time_l, order_time_r in order_time_ranges:
                        for courier_time_l, courier_time_r in courier_time_ranges:
                            # if order_time_l <= courier_time_l <= order_time_r or order_time_l <= courier_time_r <= order_time_r:
                            if courier_time_l <= order_time_l <= courier_time_r or courier_time_l <= order_time_r <= courier_time_r:
                                result = True

                    if result is True:
                        collected_weight = collected_weight + order.weight
                        res_orders.append(order)

    return res_orders

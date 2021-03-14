from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
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

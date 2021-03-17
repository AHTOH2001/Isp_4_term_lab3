from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Courier, Order


class CourierSerializer(serializers.ModelSerializer):
    regions = serializers.ListField(child=serializers.IntegerField(min_value=0))
    working_hours = serializers.ListField(child=serializers.CharField(min_length=11, max_length=11))

    class Meta:
        model = Courier
        exclude = ['assign_time', 'complete_time']


class CourierUpdateSerializer(CourierSerializer):
    def validate(self, data):
        for field in self.initial_data:
            if field not in ['courier_type', 'regions', 'working_hours']:
                raise serializers.ValidationError(f"Redundant field {field}")
        return data


class OrderSerializer(serializers.ModelSerializer):
    weight = serializers.DecimalField(max_digits=None, decimal_places=None, max_value=50, min_value=0.01 - 0.000000001)
    delivery_hours = serializers.ListField(child=serializers.CharField(min_length=11, max_length=11))

    class Meta:
        model = Order
        # fields = '__all__'
        exclude = ['taken_by', 'is_done']


class DataObject:
    def __init__(self, data):
        self.data = data


class CouriersCreateSerializer(serializers.Serializer):
    data = CourierSerializer(many=True)

    def create(self, validated_data):
        for item in validated_data['data']:
            Courier.objects.create(**item)
        return DataObject(**validated_data)


class OrdersCreateSerializer(serializers.Serializer):
    data = OrderSerializer(many=True)

    def create(self, validated_data):
        for item in validated_data['data']:
            Order.objects.create(**item)
        return DataObject(**validated_data)


# {'data': [OrderedDict([('name', 'name1'), ('courier_type', 'courier_type1')]),
#           OrderedDict([('name', 'name2'), ('courier_type', 'courier_type2')])]}


class CouriersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = '__all__'


class OrdersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


# class DataObject:
#     def __init__(self, data):
#         self.data = data

class OrdersAssignSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField(min_value=0)


class OrderCompleteSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField(min_value=0)
    order_id = serializers.IntegerField(min_value=0)
    complete_time = serializers.DateTimeField()

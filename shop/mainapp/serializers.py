from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Courier


class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = '__all__'


class DataCourier:
    def __init__(self, data):
        self.data = data


class CouriersCreateSerializer(serializers.Serializer):
    data = CourierSerializer(many=True)

    def create(self, validated_data):
        for item in validated_data['data']:
            Courier.objects.create(**item)
        return DataCourier(**validated_data)


# {'data': [OrderedDict([('name', 'name1'), ('courier_type', 'courier_type1')]),
#           OrderedDict([('name', 'name2'), ('courier_type', 'courier_type2')])]}


class CouriersListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courier
        fields = '__all__'

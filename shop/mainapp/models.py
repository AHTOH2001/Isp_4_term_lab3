from django.db import models


class Courier(models.Model):
    courier_id = models.PositiveIntegerField(verbose_name='идентификатор курьера', primary_key=True, unique=True)
    COURIER_TYPE_CHOICES = [
        ('foot', 10),
        ('bike', 15),
        ('car', 50),
    ]
    courier_type = models.CharField(verbose_name='тип курьера', max_length=255, choices=COURIER_TYPE_CHOICES)
    regions = models.JSONField(verbose_name='районы работы')
    working_hours = models.JSONField(verbose_name='рабочие часы')


class Order(models.Model):
    order_id = models.PositiveIntegerField(verbose_name='идентификатор заказа', primary_key=True, unique=True)
    weight = models.DecimalField(verbose_name='вес заказа', decimal_places=2, max_digits=4)
    region = models.PositiveIntegerField(verbose_name='район доставки')
    delivery_hours = models.JSONField(verbose_name='часы доставки')
    taken_by = models.ForeignKey(Courier, verbose_name='взят курьером', on_delete=models.CASCADE, null=True)

from django.db import models


# class Region(models.Model):
#     region_id = models.PositiveIntegerField(verbose_name='Идентификатор региона', primary_key=True, unique=True,
#                                     auto_created=True)


class Courier(models.Model):
    courier_id = models.PositiveIntegerField(verbose_name='Идентификатор курьера', primary_key=True, unique=True)
    COURIER_TYPE_CHOICES = [
        ('foot', 10),
        ('bike', 15),
        ('car', 50),
    ]
    courier_type = models.CharField(verbose_name='Тип курьера', max_length=255, choices=COURIER_TYPE_CHOICES)
    # regions = models.ManyToManyField(Region, verbose_name='Идентификаторы районов', null=True, auto_created=True)
    regions = models.JSONField(verbose_name='Идентификаторы регионов')
    working_hours = models.JSONField(verbose_name='Рабочие часы')




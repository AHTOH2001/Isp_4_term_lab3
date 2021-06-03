from django.conf.global_settings import AUTH_USER_MODEL
from django.contrib.auth.models import User, AbstractUser
from django.db import models


class CourierProfile(models.Model):
    courier_id = models.PositiveIntegerField(verbose_name='идентификатор курьера', primary_key=True, unique=True,
                                             auto_created=True)
    TYPE_TO_VALUE = {'foot': 10, 'bike': 15, 'car': 50}
    TYPE_TO_COEF = {'foot': 2, 'bike': 5, 'car': 9}
    COURIER_TYPE_CHOICES = [
        ('foot', f'Пешком ({TYPE_TO_VALUE["foot"]} kg)'),
        ('bike', f'На велосипеде ({TYPE_TO_VALUE["bike"]} kg)'),
        ('car', f'На машине ({TYPE_TO_VALUE["car"]} kg)'),
    ]
    courier_type = models.CharField(verbose_name='тип курьера', max_length=255, choices=COURIER_TYPE_CHOICES)
    regions = models.JSONField(verbose_name='районы работы')
    working_hours = models.JSONField(verbose_name='рабочие часы')
    assign_time = models.DateTimeField(verbose_name='Дата назначения заказов', null=True, blank=True)
    complete_time = models.DateTimeField(verbose_name='Дата завершения заказа', null=True, blank=True)
    time_regions = models.JSONField(verbose_name='Минимальное время доставки по району', null=True, blank=True)
    finished_amount_regions = models.JSONField(verbose_name='Количество завершенных заказов по району', null=True,
                                               blank=True)
    earning_coef = models.IntegerField(null=True, editable=True, blank=True)
    earning = models.IntegerField(default=0, editable=True)

    def __str__(self):
        return f'{self.courier_id}| {self.courier_type} курьер с {len(self.order_set.all())} заказами (зп {self.earning})'

    class Meta(AbstractUser.Meta):
        verbose_name = 'Профиль курьера'
        verbose_name_plural = 'Профили курьеров'
        # abstract = True


class Courier(models.Model):
    mobile_phone = models.CharField(max_length=28, verbose_name='Мобильный номер', null=True)
    user = models.ForeignKey(AUTH_USER_MODEL, verbose_name=User.Meta.verbose_name, on_delete=models.CASCADE, blank=True,
                             null=True)
    profile = models.OneToOneField(CourierProfile, on_delete=models.deletion.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'{getattr(self.user, "first_name")} {getattr(self.user, "last_name")}'

    class Meta(AbstractUser.Meta):
        verbose_name = 'Курьер'
        verbose_name_plural = 'Курьеры'


class Order(models.Model):
    order_id = models.PositiveIntegerField(verbose_name='идентификатор заказа', primary_key=True, unique=True)
    weight = models.DecimalField(verbose_name='вес заказа', decimal_places=2, max_digits=4)
    region = models.PositiveIntegerField(verbose_name='район доставки')
    delivery_hours = models.JSONField(verbose_name='часы доставки')
    taken_by = models.ForeignKey(CourierProfile, verbose_name='взят курьером', on_delete=models.CASCADE, null=True,
                                 blank=True)
    is_done = models.BooleanField(verbose_name='Завершён ли заказ', default=False)

    def __str__(self):
        if self.taken_by is None:
            return f'{self.order_id}| Свободный заказ'
        else:
            if self.is_done:
                is_done_verbose = 'Завершённый'
            else:
                is_done_verbose = 'Не завершённый'
            return f'{self.order_id}| {is_done_verbose} заказ курьера {self.taken_by.courier_id}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

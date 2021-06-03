from django.contrib import admin
from .models import *
from django.contrib.auth.models import User


class CourierAdmin(admin.ModelAdmin):
    # fields = ('mobile_phone', 'user')
    #
    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return qs

    list_display = ['__str__', 'user', 'profile']


admin.site.register(Courier, CourierAdmin)
admin.site.register(CourierProfile)
admin.site.register(Order)

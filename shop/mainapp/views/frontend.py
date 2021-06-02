import datetime

from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages

from ..forms import CourierRegisterForm, CourierAuthorizationForm, ProfileCreationForm
from ..settings import time_for_registration
from ..utils import get_code
from django import urls
from django.utils import timezone
import requests
from ..models import CourierProfile, Courier, Order
import logging


def home(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Перед использованием нашего чудесного сайта Вам стоит авторизоваться')
        return redirect('authorize')
    else:
        return redirect('profile')


def register(request):
    if request.method == 'POST':
        form = CourierRegisterForm(data=request.POST)
        if form.is_valid():
            courier, raw_pass = form.save()

            confirmation_url = request.META["HTTP_HOST"] + urls.reverse(
                register_complete) + f'?login={courier.user.email}&code={get_code(courier.user.email, "abs", 20)}'
            email_message = f'''Здравствуйте, уважаемый {courier.user.last_name} {courier.user.first_name}!

Вы в одном шаге от завершения регистрации в интернет курьерне.

Ваши данные для авторизации в системе:

Логин: {courier.user.email}
Пароль: {raw_pass}

Внимание! Вы должны подтвердить регистрационные данные!
Для подтверждения достаточно перейти по следующей ссылке:

{confirmation_url}

Если Вы действительно желаете подтвердить регистрацию, пожалуйста, сделайте это до {(timezone.localtime() + time_for_registration).strftime('%H:%M %d.%m.%Y')}. В противном случае Ваши регистрационные данные будут удалены из системы.

С уважением, администрация курьерни'''

            send_mail(
                f'Подтверждение регистрации на сайте {request.META["HTTP_HOST"]}',
                email_message,
                'CheekLitBot@gmail.com',
                [courier.user.email],
                fail_silently=False,
            )
            messages.success(request, 'Пользователь успешно создан, проверьте почту и подтвердите регистрацию')
            return redirect('home')
        else:
            messages.error(request, 'Некоторые данные введены неверно')
    else:
        form = CourierRegisterForm()
    return render(request, 'register.html', {'form': form})


def register_complete(request):
    try:
        email = request.GET['login']
        code = request.GET['code'].replace(' ', '+')
        if get_code(email, 'abs', 20) == code:
            # Delete outdated clients
            User.objects.filter(date_joined__lt=timezone.localtime() - time_for_registration,
                                is_active=False, is_staff=False, is_superuser=False).delete()
            try:
                if User.objects.get(email=email).is_active is True:
                    messages.warning(request, 'Курьер уже подтверждён')
                else:
                    messages.success(request, 'Курьер успешно подтверждён, осталось только авторизоваться')
                    User.objects.filter(email=email).update(is_active=True)
                    return redirect('authorize')
            except User.DoesNotExist:
                messages.error(request, 'По всей видимости ссылка регистрации просрочена')
        else:
            messages.error(request, f'Параметр code неверный')

    except MultiValueDictKeyError as e:
        messages.error(request, f'Пропущен параметр {e.args}')

    return redirect('home')


def authorize(request):
    if request.method == 'POST':
        form = CourierAuthorizationForm(data=request.POST)
        if form.is_valid():
            courier = form.get_user()
            login(request, courier)
            messages.success(request, f'Добро пожаловать, {courier.last_name} {courier.first_name}')
            return redirect('home')
        else:
            messages.error(request, 'Некоторые данные введены неверно')
    else:
        form = CourierAuthorizationForm()
    return render(request, 'authorize.html', {'form': form})


def client_logout(request):
    logout(request)
    return redirect('home')


def profile(request):
    if not hasattr(request.user, 'courier_set'):
        return redirect('register')
    else:
        courier = request.user.courier_set.get()
        if courier.profile is None:
            return redirect('profile_create')

        if request.method == 'POST':
            if 'get_new_orders' in request.GET:
                response = requests.post(f'http://{request.META["HTTP_HOST"]}/orders/assign', json={
                    "courier_id": courier.profile.courier_id
                })
                if not response.ok:
                    messages.error(request, response.text)
                    return redirect('profile')
                else:
                    # result = [res['id'] for res in response.json()['orders']]
                    result = response.json()['orders']
                    if len(result) == 0:
                        messages.warning(request, 'Для Вас подходящих заказов пока нет')
                    else:
                        messages.success(request, f'Новые заказы: {" ".join(map(str, result))}')

            if 'complete_order' in request.GET:
                response = requests.post(f'http://{request.META["HTTP_HOST"]}/orders/complete', json={
                    "courier_id": courier.profile.courier_id,
                    "order_id": request.GET['complete_order'],
                    "complete_time": str(timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
                })
                if not response.ok:
                    messages.error(request, response.text)
                    return redirect('profile')
                else:
                    messages.success(request, response.text)

    response = requests.get(f'http://{request.META["HTTP_HOST"]}/couriers/{courier.profile.courier_id}')
    if not response.ok:
        messages.error(request, response.text)
        return redirect('register')
    else:
        context = response.json()
        context['courier'] = courier
        verbose_choices = dict(CourierProfile.COURIER_TYPE_CHOICES)
        context['courier_type'] = verbose_choices[context['courier_type']]
        context['uncompleted_orders'] = courier.profile.order_set.filter(is_done=False)
        context['completed_orders'] = courier.profile.order_set.filter(is_done=True)

        return render(request, 'profile.html', context)


def profile_create(request):
    if request.method == 'POST':
        form = ProfileCreationForm(data=request.POST)
        if form.is_valid():

            courier_profile = form.save(commit=False)
            response = requests.post(f'http://{request.META["HTTP_HOST"]}/couriers', json={
                "data": [
                    {
                        "courier_id": courier_profile.courier_id,
                        "courier_type": courier_profile.courier_type,
                        "regions": courier_profile.regions,
                        "working_hours": courier_profile.working_hours
                    }
                ]
            })

            if not response.ok:
                logging.error(response.text)
                messages.error(request, response.text)
            else:
                actual_courier_profile = CourierProfile.objects.get(courier_id=courier_profile.courier_id)
                Courier.objects.filter(id=request.user.courier_set.get().id).update(profile=actual_courier_profile)
                messages.success(request, f'Профиль успешно создан')
            return redirect('profile')
        else:
            logging.error('Некоторые данные введены неверно')
            messages.error(request, 'Некоторые данные введены неверно')
    else:
        form = ProfileCreationForm()
    return render(request, 'profile_create.html', {'form': form})


def useful_information(request):
    return render(request, 'useful_information.html')


def about_us(request):
    return render(request, 'about_us.html')


def contact(request):
    return render(request, 'contact.html')


def edit(request):
    current_profile = request.user.courier_set.get().profile
    if request.method == 'POST':
        form = ProfileCreationForm(data=request.POST)
        if form.is_valid():
            courier_profile = form.save(commit=False)
            response = requests.patch(f'http://{request.META["HTTP_HOST"]}/couriers/{current_profile.courier_id}',
                                      json={
                                          "courier_type": courier_profile.courier_type,
                                          "regions": courier_profile.regions,
                                          "working_hours": courier_profile.working_hours
                                      })

            if not response.ok:
                messages.error(request, response.text)
            else:
                # actual_courier_profile = CourierProfile.objects.get(courier_id=courier_profile.courier_id)
                # Courier.objects.filter(id=request.user.courier_set.get().id).update(profile=actual_courier_profile)
                messages.success(request, f'Профиль успешно отредактирован')
            return redirect('profile')
        else:
            messages.error(request, 'Некоторые данные введены неверно')
    else:
        form = ProfileCreationForm(
            data={'courier_type': str(current_profile.courier_type), 'regions': str(current_profile.regions),
                  'working_hours': str(current_profile.working_hours).replace("'", '"')})
    return render(request, 'profile_edit.html', {'form': form})

import datetime

from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages

from ..forms import CourierRegisterForm, CourierAuthorizationForm, ProfileCreationForm, CreateOrderForm
from ..utils import get_code
from django import urls
from django.utils import timezone
from rest_framework.authtoken.models import Token
import requests
from ..models import CourierProfile, Courier, Order
import logging
from shop.settings import time_for_registration, logging_level, log_file
import threading

logging.basicConfig(filename=log_file, level=getattr(logging, logging_level))


def home(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Перед использованием нашего чудесного сайта Вам стоит авторизоваться')
        logging.info('Перед использованием нашего чудесного сайта Вам стоит авторизоваться')
        return redirect('authorize')
    else:
        return redirect('profile')


def register(request):
    if request.method == 'POST':
        form = CourierRegisterForm(data=request.POST)
        if form.is_valid():
            try:
                User.objects.get(email=request.POST['email'])
            except User.DoesNotExist:
                pass
            else:
                logging.info('Некоторые данные введены неверно')
                messages.error(request, 'Такой Email уже зарегистрирован')
                return render(request, 'register.html', {'form': form})
            courier, raw_pass = form.save()

            confirmation_url = request.META["REMOTE_ADDR"] + ':' + request.META["SERVER_PORT"] + urls.reverse(
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

            thread = threading.Thread(target=send_mail, args=(
                f'Подтверждение регистрации на сайте {request.META["REMOTE_ADDR"] + ":" + request.META["SERVER_PORT"]}',
                email_message,
                'CheekLitBot@gmail.com',
                [courier.user.email]), kwargs={'fail_silently': False})
            thread.start()
            messages.success(request, 'Пользователь успешно создан, проверьте почту и подтвердите регистрацию')
            logging.info('Пользователь успешно создан, проверьте почту и подтвердите регистрацию')
            return redirect('authorize')
        else:
            logging.info('Некоторые данные введены неверно')
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
                    logging.info('Курьер уже подтверждён')
                else:
                    messages.success(request, 'Курьер успешно подтверждён, осталось только авторизоваться')
                    logging.info('Курьер успешно подтверждён, осталось только авторизоваться')
                    User.objects.filter(email=email).update(is_active=True)
                    return redirect('authorize')
            except User.DoesNotExist:
                messages.error(request, 'По всей видимости ссылка регистрации просрочена')
                logging.error('По всей видимости ссылка регистрации просрочена')
        else:
            messages.error(request, f'Параметр code неверный')
            logging.error(f'Параметр code неверный')

    except MultiValueDictKeyError as e:
        messages.error(request, f'Пропущен параметр {e.args}')
        logging.error(f'Пропущен параметр {e.args}')

    return redirect('authorize')


def authorize(request):
    if request.method == 'POST':
        form = CourierAuthorizationForm(data=request.POST)
        if form.is_valid():
            courier = form.get_user()
            login(request, courier)
            messages.success(request, f'Добро пожаловать, {courier.last_name} {courier.first_name}')
            logging.info(f'Добро пожаловать, {courier.last_name} {courier.first_name}')
            return redirect('home')
        else:
            messages.error(request, 'Некоторые данные введены неверно')
            logging.info('Некоторые данные введены неверно')
    else:
        form = CourierAuthorizationForm()
    return render(request, 'authorize.html', {'form': form})


def client_logout(request):
    logout(request)
    messages.warning(request, 'До встречи!')
    logging.info('До встречи!')
    return redirect('authorize')


def profile(request):
    try:
        courier = request.user.courier_set.get()
    except Courier.DoesNotExist:
        messages.warning(request, 'Курьер не найден')
        return redirect('register')
    else:
        if courier.profile is None:
            return redirect('profile_create')

        if request.method == 'POST':
            if 'get_new_orders' in request.GET:
                token, created = Token.objects.get_or_create(user=request.user)
                response = requests.post(
                    f'http://{request.META["REMOTE_ADDR"] + ":" + request.META["SERVER_PORT"]}/orders/assign', json={
                        "courier_id": courier.profile.courier_id,
                        'token': token.key,
                        'user_id': request.user.id
                    })
                if not response.ok:
                    messages.error(request, response.text)
                    logging.error(response.text)
                    return redirect('profile')
                else:
                    # result = [res['id'] for res in response.json()['orders']]
                    result = response.json()['orders']
                    if len(result) == 0:
                        messages.warning(request, 'Для Вас подходящих заказов пока нет')
                        logging.info('Для Вас подходящих заказов пока нет')
                    else:
                        messages.success(request, f'Новые заказы: {" ".join(map(str, result))}')
                        logging.info(f'Новые заказы: {" ".join(map(str, result))}')

            if 'complete_order' in request.GET:
                token, created = Token.objects.get_or_create(user=request.user)
                response = requests.post(
                    f'http://{request.META["REMOTE_ADDR"] + ":" + request.META["SERVER_PORT"]}/orders/complete', json={
                        "courier_id": courier.profile.courier_id,
                        "order_id": request.GET['complete_order'],
                        "complete_time": str(timezone.localtime().strftime('%Y-%m-%dT%H:%M:%S.%fZ')),
                        'token': token.key,
                        'user_id': request.user.id
                    })
                if not response.ok:
                    messages.error(request, response.text)
                    logging.info(response.text)
                    return redirect('profile')
                else:
                    messages.success(request, response.text)
                    logging.info(response.text)

    token, created = Token.objects.get_or_create(user=request.user)
    response = requests.get(
        f'http://{request.META["REMOTE_ADDR"] + ":" + request.META["SERVER_PORT"]}/couriers/{courier.profile.courier_id}',
        json={
            'token': token.key,
            'user_id': request.user.id
        })
    if not response.ok:
        messages.error(request, response.text)
        logging.info(response.text)
        return redirect('register')
    else:
        context = response.json()
        context['courier'] = request.user.courier_set.get()
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
            token, created = Token.objects.get_or_create(user=request.user)
            response = requests.post(
                f'http://{request.META["REMOTE_ADDR"] + ":" + request.META["SERVER_PORT"]}/couriers', json={
                    "data": [
                        {
                            "courier_id": courier_profile.courier_id,
                            "courier_type": courier_profile.courier_type,
                            "regions": courier_profile.regions,
                            "working_hours": courier_profile.working_hours,
                        }
                    ],
                    'token': token.key,
                    'user_id': request.user.id
                })

            if not response.ok:
                logging.info(response.text)
                messages.error(request, response.text)
                return render(request, 'profile_create.html', {'form': form})
            else:
                actual_courier_profile = CourierProfile.objects.get(courier_id=courier_profile.courier_id)
                Courier.objects.filter(id=request.user.courier_set.get().id).update(profile=actual_courier_profile)
                messages.success(request, f'Профиль успешно создан')
                logging.info(f'Профиль успешно создан')
            return redirect('profile')
        else:
            logging.info('Некоторые данные введены неверно')
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
            token, created = Token.objects.get_or_create(user=request.user)
            response = requests.patch(
                f'http://{request.META["REMOTE_ADDR"] + ":" + request.META["SERVER_PORT"]}/couriers/{current_profile.courier_id}',
                json={
                    "courier_type": courier_profile.courier_type,
                    "regions": courier_profile.regions,
                    "working_hours": courier_profile.working_hours,
                    'token': token.key,
                    'user_id': request.user.id
                })

            if not response.ok:
                messages.error(request, response.text)
                logging.info(response.text)
            else:
                # actual_courier_profile = CourierProfile.objects.get(courier_id=courier_profile.courier_id)
                # Courier.objects.filter(id=request.user.courier_set.get().id).update(profile=actual_courier_profile)
                messages.success(request, f'Профиль успешно отредактирован')
                logging.info(f'Профиль успешно отредактирован')
            return redirect('profile')
        else:
            messages.error(request, 'Некоторые данные введены неверно')
            logging.info('Некоторые данные введены неверно')
    else:
        form = ProfileCreationForm(
            data={'courier_type': str(current_profile.courier_type), 'regions': str(current_profile.regions),
                  'working_hours': str(current_profile.working_hours).replace("'", '"')})
    return render(request, 'profile_edit.html', {'form': form})


def create_order(request):
    if not request.user.is_staff:
        return redirect('home')

    if request.method == 'POST':
        form = CreateOrderForm(data=request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            token, created = Token.objects.get_or_create(user=request.user)
            response = requests.post(f'http://{request.META["REMOTE_ADDR"] + ":" + request.META["SERVER_PORT"]}/orders',
                                     json={
                                         "data": [
                                             {
                                                 "order_id": order.order_id,
                                                 "weight": float(order.weight),
                                                 "region": order.region,
                                                 "delivery_hours": order.delivery_hours
                                             }
                                         ],
                                         'token': token.key,
                                         'user_id': request.user.id
                                     })
            if response.ok:
                messages.success(request, 'Заказ успешно создан')
                logging.info('Заказ успешно создан')
                return render(request, 'order_create.html', {'form': CreateOrderForm()})
            else:
                messages.error(request, f'Ошибка: {response.text}')
                logging.info(f'Ошибка: {response.text}')
        else:
            messages.error(request, 'Некоторые данные введены неверно')
            logging.info('Некоторые данные введены неверно')
    else:
        form = CreateOrderForm()

    return render(request, 'order_create.html', {'form': form})

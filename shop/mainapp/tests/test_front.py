from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from mainapp.models import CourierProfile, Order, CourierProfile, Courier
from django.test import Client
from django.utils import timezone
from rest_framework.authtoken.models import Token
import requests


# raise Exception((response.content, response.status_code))

class RestFront(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create(username='test_admin', password='test', is_staff=True, is_superuser=True,
                                             is_active=True)
        profile = CourierProfile.objects.create(**{"courier_id": 1,
                                                   "courier_type": 'foot',
                                                   "regions": [4, 6, 13],
                                                   "working_hours": ['10:20-14:30', '16:00-18:00']
                                                   })
        user1 = User.objects.create(username='test1@gmail.com', password='test', email='test1@gmail.com',
                                    is_active=True)
        cls.courier_without_profile = Courier.objects.create(mobile_phone='+3278427', user=user1)
        user2 = User.objects.create(username='test2@gmail.com', password='test', email='test2@gmail.com',
                                    is_active=True)
        cls.courier_with_profile = Courier.objects.create(mobile_phone='+3278427', user=user2, profile=profile)

    def test_home_page(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/authorize/')

        self.client.force_login(user=self.admin_user)
        response = self.client.get('')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/profile/')

    def test_register_page(self):
        response = self.client.post('/register/', {
            'email': 'hren'
        })
        self.assertNotEqual(response.status_code, 302)

        response = self.client.post('/register/', {
            'email': 'norm@mail.ru',
            'first_name': 'first ivan',
            'last_name': 'last ivan',
            'mobile_phone': '+483958934',
            'password': 'fhs832467981h73'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/authorize/')

    def test_register_comp(self):
        response = self.client.get('/register/complete/', {
            'email': 'hren',
            'code': 'hren'
        })
        self.assertEqual(response.status_code, 302)

    def test_authorize(self):
        response = self.client.get('/authorize/', {
            'email': 'hren',
            'password': 'hren'
        })
        self.assertNotEqual(response.status_code, 302)

        response = self.client.post('/authorize/', {
            'username': 'test1@gmail.com',
            'password': 'test'
        })
        self.assertNotEqual(response.status_code, 302)

    def test_client_logout(self):
        self.client.force_login(user=self.courier_without_profile.user)
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)

    def test_profile(self):
        try:
            self.client.get('/profile/')
        except AttributeError:
            pass

        self.client.force_login(user=self.courier_without_profile.user)
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)

        self.client.force_login(user=self.courier_without_profile.user)
        try:
            response = self.client.get('/profile/')
        except requests.exceptions.ConnectionError:
            pass
        else:
            self.assertEqual(response.status_code, 302)

    def test_edit(self):
        self.client.force_login(user=self.courier_with_profile.user)
        response = self.client.post('/profile/edit/', {
            'courier_type': 'hren',
            'regions': '[4, 2, 6]',
            'working_hours': '["10:00-18:00"]'
        })

        self.assertNotEqual(response.status_code, 302)
        try:
            response = self.client.post('/profile/edit/', {
                'courier_type': 'foot',
                'regions': '[4, 2, 6]',
                'working_hours': '["10:00-18:00"]'
            })
        except requests.exceptions.ConnectionError:
            pass
        else:
            self.assertEqual(response.status_code, 302)

    def test_create_order(self):

        response = self.client.post('/order/create', {
            'weight': '12',
            'region': '5',
            'delivery_hours': '["10:00-18:00"]'
        })
        self.assertEqual(response.status_code, 302)

        self.client.force_login(user=self.admin_user)
        response = self.client.post('/order/create', {
            'weight': '9999',
            'region': '5',
            'delivery_hours': '["10:00-18:00"]'
        })
        self.assertNotEqual(response.status_code, 302)

        try:
            response = self.client.post('/order/create', {
                'weight': '12',
                'region': '5',
                'delivery_hours': '["10:00-18:00"]'
            })
        except requests.exceptions.ConnectionError:
            pass
        else:
            self.assertNotEqual(response.status_code, 302)

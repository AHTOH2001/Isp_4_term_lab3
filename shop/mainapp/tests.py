from datetime import datetime

from django.test import TestCase
from rest_framework import status
from .models import CourierProfile, Order
from django.test import Client
from django.utils import timezone


# raise Exception((response.content, response.status_code))

class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        CourierProfile.objects.create(
            courier_id=1,
            courier_type="foot",
            regions=[1, 12, 22],
            working_hours=["11:35-14:05", "09:00-11:00"]
        )
        CourierProfile.objects.create(
            courier_id=2,
            courier_type="bike",
            regions=[1, 22],
            working_hours=["09:00-18:00"]
        )
        CourierProfile.objects.create(
            courier_id=3,
            courier_type="car",
            regions=[12, 22, 23, 33],
            working_hours=["20:35-23:05"]
        )

        Order.objects.create(
            order_id=1,
            weight=0.23,
            region=12,
            delivery_hours=["09:00-18:00"]
        )
        Order.objects.create(
            order_id=2,
            weight=5,
            region=1,
            delivery_hours=["09:00-18:00"]
        )
        Order.objects.create(
            order_id=3,
            weight=14.01,
            region=22,
            delivery_hours=["09:00-12:00", "16:00-21:30"]
        )
        Order.objects.create(
            order_id=4,
            weight=2.05,
            region=22,
            delivery_hours=["09:00-11:00"]
        )
        Order.objects.create(
            order_id=5,
            weight=3,
            region=23,
            delivery_hours=["09:00-11:00"]
        )
        Order.objects.create(
            order_id=6,
            weight=1.5,
            region=12,
            delivery_hours=["21:00-22:00"]
        )

    def test_success_order_create(self):
        response = self.client.post('/orders', {
            "data": [
                {
                    "order_id": 10,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(response.content, {"orders": [{"id": 10}]})

    def test_success_courier_create(self):
        response = self.client.post('/couriers', {
            "data": [
                {
                    "courier_id": 4,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(response.content, {"couriers": [{"id": 4}]})

    def test_bad_courier_create(self):
        response = self.client.post('/couriers', {
            "data": [
                {
                    "courier_id": 5,
                    "courier_type": "foot",
                    "regions": [1, 12, 22]
                },
                {
                    "courier_id": 6,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 8,
                    "courier_type": "footage",
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, {"validation_error": {"couriers": [{"id": 5}, {"id": 8}]}})

    def test_bad_order_create(self):
        response = self.client.post('/orders', {
            "data": [
                {
                    "order_id": 8,
                    "weight": 50.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 9,
                    "weight": 11,
                    "region": 5,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 10,
                    "weight": 0.001,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                },
                {
                    "order_id": 1,
                    "weight": 0.5,
                    "region": 20,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(response.content, {"validation_error": {"orders": [{"id": 8}, {"id": 10}, {"id": 1}]}})

    def test_bad_courier_get(self):
        response = self.client.get('/couriers/4')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_success_courier_get(self):
        response = self.client.get('/couriers/2')
        self.assertJSONEqual(response.content,
                             {"courier_id": 2, "courier_type": "bike", "regions": [1, 22],
                              "working_hours": ["09:00-18:00"], "earning": 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_courier_patch_create(self):
        response = self.client.patch('/couriers/2', {
            "regions": [11, 2, 12],
            "working_hours": ["09:00-15:00"]
        }, content_type='application/json')

        self.assertJSONEqual(response.content,
                             {"courier_id": 2, "courier_type": "bike", "regions": [11, 2, 12],
                              "working_hours": ["09:00-15:00"],
                              })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/couriers/2')
        self.assertJSONEqual(response.content,
                             {"courier_id": 2, "courier_type": "bike", "regions": [11, 2, 12],
                              "working_hours": ["09:00-15:00"], "earning": 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch('/couriers/13', {
            "regions": [11, 2, 12],
            "working_hours": ["09:00-15:00"]
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch('/couriers/2', {"strange_field": 123}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_couriers(self):
        response = self.client.post('/orders/assign', {"courier_id": 2}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.content.startswith(b'{"orders":[{"id":4},{"id":2}],"assign_time":"'))

        response = self.client.post('/orders/assign', {"courier_id": 2}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.content.startswith(b'{"orders":[{"id":4},{"id":2}],"assign_time":"'))

        response = self.client.post('/orders/assign', {"courier_id": 1}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.content.startswith(b'{"orders":[{"id":1}],"assign_time":"'))

        response = self.client.post('/orders/assign', {"courier_id": 3}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.content.startswith(b'{"orders":[{"id":6},{"id":3}],"assign_time":"'))

        response = self.client.post('/orders/assign', {"courier_id": 5}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bad_complete_couriers(self):
        response = self.client.post('/orders/complete', {
            "courier_id": 1,
            "order_id": 8,
            "complete_time": "2021-03-18T18:18:01.42Z"
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post('/orders/complete', {
            "courier_id": 15,
            "order_id": 2,
            "complete_time": "2021-03-18T18:18:01.42Z"
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post('/orders/complete', {
            "courier_id": 1,
            "order_id": 8,
            "complete_time": "2021-03-18T18:18:01.42Z"
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post('/orders/complete', {
            "courier_id": 1,
            "order_id": 2,
            "complete_time": "2021-03-18T18:18:01.42Z"
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post('/orders/assign', {"courier_id": 2}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.content.startswith(b'{"orders":[{"id":4},{"id":2}],"assign_time":"'))

        response = self.client.post('/orders/complete', {
            "courier_id": 2,
            "order_id": 4,
            "complete_time": "2021-03-18T18:18:01.42Z"
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(response.content, {"order_id": 4})

        response = self.client.post('/orders/complete', {
            "courier_id": 2,
            "order_id": 4,
            "complete_time": "2021-03-18T18:18:01.42Z"
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post('/orders/complete', {
            "courier_id": 3,
            "order_id": 2,
            "complete_time": "2021-03-18T18:18:01.42Z"
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_couriers(self):
        response = self.client.post('/orders/assign', {"courier_id": 2}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.content.startswith(b'{"orders":[{"id":4},{"id":2}],"assign_time":"'))

        response = self.client.post('/orders/complete', {
            "courier_id": 2,
            "order_id": 4,
            "complete_time": "2021-03-18T18:18:01.42Z"
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(response.content, {"order_id": 4})

        response = self.client.post('/orders/assign', {"courier_id": 2}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.content.startswith(b'{"orders":[{"id":2}],"assign_time":"'))

        response = self.client.post('/orders/complete', {
            "courier_id": 2,
            "order_id": 2,
            "complete_time": "2021-03-18T18:18:01.42Z"
        }, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(response.content, {"order_id": 2})

        response = self.client.post('/orders/assign', {"courier_id": 2}, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.content.startswith(b'{"orders":[{"id":3}],"assign_time":"'))

        response = self.client.get('/couriers/2')
        self.assertTrue(response.content.endswith(b',"earning":5000}'))

        # raise Exception((response.content, response.status_code))

    def test_dublicate_couriers(self):
        response = self.client.post('/couriers', {
            "data": [
                {
                    "courier_id": 11,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 11,
                    "courier_type": "bike",
                    "regions": [22],
                    "working_hours": ["09:00-18:00"]
                },
                {
                    "courier_id": 3,
                    "courier_type": "car",
                    "regions": [12, 22, 23, 33],
                    "working_hours": []
                }
            ]
        }, content_type='application/json')

        self.assertEqual(response.status_code, 400)

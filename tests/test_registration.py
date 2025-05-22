from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestRegistration(APITestCase):

    def test_registration_success(self):
        url = reverse('registration')
        data = {
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["username"], "exampleUsername")
        self.assertEqual(response.data["email"], "example@mail.de")
        self.assertIn("user_id", response.data)
        self.assertIsInstance(response.data["user_id"], int)

    def test_registration_invalid_data(self):
        url = reverse('registration')
        # username is missing
        data = {
            "username": "",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
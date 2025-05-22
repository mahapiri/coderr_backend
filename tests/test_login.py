from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from user_auth_app.models import Profile


class TestLogin(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="exampleUsername", email="example@test.de", password="Hallo123@")
        self.profile = Profile.objects.create(type="business", user=self.user)
        self.token = Token.objects.get_or_create(user=self.user)
        # client = APIClient()
        # client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_login_success(self):
        url = reverse("login")
        data = {
            "username": "exampleUsername",
            "password": "Hallo123@",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid_data(self):
        # PW ist not correct
        url = reverse("login")
        data = {
            "username": "exampleUsername",
            "password": "Hallo123",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

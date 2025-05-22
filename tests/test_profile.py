from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from user_auth_app.models import Profile


class TestProfile(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="exampleUsername", email="example@test.de", password="Hallo123@")
        self.profile = Profile.objects.create(type="business", user=self.user)
        self.token, created = Token.objects.get_or_create(user=self.user)

    def test_get_profile(self):
        url = reverse("profile-detail", args=[self.profile.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_profile_not_authorized(self):
        url = reverse("profile-detail", args=[self.profile.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_not_exist_profile(self):
        url = reverse("profile-detail", args=[self.profile.id+1])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
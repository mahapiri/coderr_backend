from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from user_auth_app.models import Profile


class TestGetProfile(APITestCase):

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
        url = reverse("profile-detail", args=[self.profile.id+10])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TestUpdateProfile(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="exampleUsername", email="example@test.de", password="Hallo123@")
        self.profile = Profile.objects.create(type="business", user=self.user)
        self.token, created = Token.objects.get_or_create(user=self.user)

        self.otherUser = User.objects.create_user(
            username="exampleUsernameOther", email="exampleother@test.de", password="Hallo123@")
        self.otherProfile = Profile.objects.create(type="business", user=self.otherUser)
        self.otherToken, created = Token.objects.get_or_create(user=self.otherUser)

    def test_update_own_profile(self):
        url = reverse("profile-detail", args=[self.profile.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.user = User.objects.update(first_name="Testperson", last_name="Nachname", email="pjs@test.de")
        self.profile = Profile.objects.update(location="Berlin", tel="07954223", description="Test Description", working_hours="9-12")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_profile_not_authorized(self):
        url = reverse("profile-detail", args=[self.profile.id])
        self.user = User.objects.update(first_name="Testperson", last_name="Nachname", email="pjs@test.de")
        self.profile = Profile.objects.update(location="Berlin", tel="07954223", description="Test Description", working_hours="9-12")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile_other_profile(self):
        url = reverse("profile-detail", args=[self.otherProfile.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)      
        self.otherUser = User.objects.update(first_name="Testperson", last_name="Nachname", email="pjs@test.de")
        self.otherProfile = Profile.objects.update(location="Berlin", tel="07954223", description="Test Description", working_hours="9-12")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_not_exist_profile(self):
        url = reverse("profile-detail", args=[self.profile.id+10])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.user = User.objects.update(first_name="Testperson", last_name="Nachname", email="pjs@test.de")
        self.profile = Profile.objects.update(location="Berlin", tel="07954223", description="Test Description", working_hours="9-12")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
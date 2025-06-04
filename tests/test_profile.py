from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from user_auth_app.models import Profile


# Test class for retrieving profiles
class TestGetProfile(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="exampleUsername", email="example@test.de", password="Hallo123@")
        self.profile = Profile.objects.create(type="business", user=self.user)
        self.token, created = Token.objects.get_or_create(user=self.user)

    # Test successfully retrieving a profile with valid token
    def test_get_profile(self):
        url = reverse("profile-detail", args=[self.profile.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test retrieving a profile without authorization
    def test_get_profile_not_authorized(self):
        url = reverse("profile-detail", args=[self.profile.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # Test retrieving a non-existent profile
    def test_get_not_exist_profile(self):
        url = reverse("profile-detail", args=[self.profile.id+10])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# Test class for updating profiles
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

    # Test updating own profile with authorization
    def test_update_own_profile(self):
        url = reverse("profile-detail", args=[self.profile.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.user = User.objects.update(first_name="Testperson", last_name="Nachname", email="pjs@test.de")
        self.profile = Profile.objects.update(location="Berlin", tel="07954223", description="Test Description", working_hours="9-12")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test updating own profile without authorization
    def test_update_profile_not_authorized(self):
        url = reverse("profile-detail", args=[self.profile.id])
        self.user = User.objects.update(first_name="Testperson", last_name="Nachname", email="pjs@test.de")
        self.profile = Profile.objects.update(location="Berlin", tel="07954223", description="Test Description", working_hours="9-12")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Test trying to update another user's profile
    def test_update_profile_other_profile(self):
        url = reverse("profile-detail", args=[self.otherProfile.id])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)      
        self.otherUser = User.objects.update(first_name="Testperson", last_name="Nachname", email="pjs@test.de")
        self.otherProfile = Profile.objects.update(location="Berlin", tel="07954223", description="Test Description", working_hours="9-12")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test updating a non-existent profile
    def test_update_not_exist_profile(self):
        url = reverse("profile-detail", args=[self.profile.id+10])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.user = User.objects.update(first_name="Testperson", last_name="Nachname", email="pjs@test.de")
        self.profile = Profile.objects.update(location="Berlin", tel="07954223", description="Test Description", working_hours="9-12")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# Test class for listing business profiles
class TestBusinessProfile(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="exampleUsername", email="example@test.de", password="Hallo123@")
        self.profile = Profile.objects.create(type="business", user=self.user)
        self.token, created = Token.objects.get_or_create(user=self.user)

    # Test retrieving all business profiles with authorization
    def test_get_business(self):
        url = reverse("business_profiles")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test retrieving business profiles without authorization
    def test_get_business_profil_not_authorized(self):
        url = reverse("business_profiles")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# Test class for listing customer profiles       
class TestCustomerProfile(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="exampleUsername", email="example@test.de", password="Hallo123@")
        self.profile = Profile.objects.create(type="business", user=self.user)
        self.token, created = Token.objects.get_or_create(user=self.user)

    # Test retrieving all customer profiles with authorization
    def test_get_business(self):
        url = reverse("customer_profiles")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test retrieving business profiles without authorization
    def test_get_business_profil_not_authorized(self):
        url = reverse("business_profiles")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
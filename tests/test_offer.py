from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


# Test class for offers (Offer)
class TestOffer(APITestCase):

    # Helper method to get offer creator IDs
    def get_offer_creator_id(self):
        url = reverse("offers", args=[])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
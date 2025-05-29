from django.urls import path
from rest_framework.routers import DefaultRouter

from offer_app.api.views import OfferViewSet


router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename="offers")

urlpatterns = [ ]

urlpatterns += router.urls
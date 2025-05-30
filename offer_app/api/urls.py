from django.urls import path
from rest_framework.routers import DefaultRouter

from offer_app.api.views import OfferDetailView, OfferViewSet


router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename="offers")

urlpatterns = [ 
    path("offerdetails/<int:pk>/", OfferDetailView.as_view({"get": "retrieve"}), name="offerdetail")
]

urlpatterns += router.urls
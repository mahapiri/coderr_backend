from django.urls import path
from rest_framework.routers import DefaultRouter

from review_app.api.views import ReviewViewSet


router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename="reviews")

urlpatterns = []

urlpatterns += router.urls
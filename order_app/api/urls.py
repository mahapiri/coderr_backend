from django.urls import path
from rest_framework.routers import DefaultRouter

from order_app.api.views import OrderViewSet


router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename="orders")

urlpatterns = [ 
]

urlpatterns += router.urls
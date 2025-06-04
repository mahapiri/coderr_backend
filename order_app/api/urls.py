from django.urls import path
from rest_framework.routers import DefaultRouter

from order_app.api.views import CompletedOrderView, OrderCountView, OrderViewSet


# Router for registering viewsets
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename="orders")

# URL patterns for order-related endpoints
urlpatterns = [
    path("order-count/<int:business_user_id>/", OrderCountView.as_view(), name="order-count"), 
    path("completed-order-count/<int:business_user_id>/", CompletedOrderView.as_view(), name="completed-order"), 
]

# Add router URLs to urlpatterns
urlpatterns += router.urls
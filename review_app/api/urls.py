from rest_framework.routers import DefaultRouter

from review_app.api.views import ReviewViewSet


# Register the ReviewViewSet with the DefaultRouter
router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename="reviews")

urlpatterns = []

urlpatterns += router.urls
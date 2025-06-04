from django.urls import path

from rest_framework.routers import DefaultRouter

from user_auth_app.api.views import CustomerListView, ProfilLoginView, ProfilRegistrationView, ProfileViewSet, BusinessListView


# Register the ProfileViewSet with the DefaultRouter
router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename="profile")

# Define URL patterns for user authentication and profile-related endpoints
urlpatterns = [
    path("registration/", ProfilRegistrationView.as_view(), name="registration"),
    path("login/", ProfilLoginView.as_view(), name="login"),
    path("profiles/business/", BusinessListView.as_view(), name="business_profiles"),
    path("profiles/customer/", CustomerListView.as_view(), name="customer_profiles"),
]

urlpatterns += router.urls
from django.urls import path
from rest_framework.routers import DefaultRouter

from user_auth_app.api.views import ProfilLoginView, ProfilRegistrationView, ProfileViewSet

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename="profile")

urlpatterns = [
    path("registration/", ProfilRegistrationView.as_view(), name="registration"),
    path("login/", ProfilLoginView.as_view(), name="login"),
]

urlpatterns += router.urls
"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from core.api.views import BaseInfoViewSet

# URL patterns for the Django project.
# Maps URL routes to their corresponding views or included URL configs.
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include("user_auth_app.api.urls")),
    path("api/", include("offer_app.api.urls")),
    path("api/", include("order_app.api.urls")),
    path("api/", include("review_app.api.urls")),
    path("api/base-info/", BaseInfoViewSet.as_view(), name="base-info"),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    re_path(r"favicon\.ico$", RedirectView.as_view(
        url="/static/favicon.png", permanent=True)),
]

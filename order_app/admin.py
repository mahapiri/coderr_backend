from django.contrib import admin

from order_app.models import Order

# Registers the Order model in the Django admin site.
admin.site.register(Order)

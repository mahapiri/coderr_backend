from django.db import models

from offer_app.models import Offer, OfferDetail
from user_auth_app.models import Profile

STATUS_CHOICE = {
    "in_progress": "In Progress",
    "completed": "Completed",
    "cancelled": "Cancelled"
}
class Order(models.Model):
    customer_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="orders_as_customer")
    business_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="orders_as_business")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE, null=True, blank=True, related_name="orders")
    status = models.CharField(max_length=255, choices=STATUS_CHOICE, default="in_progress")

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["customer_user"]

    def __str__(self):
        return self.customer_user.user.username

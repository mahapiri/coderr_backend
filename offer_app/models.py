from django.db import models

from user_auth_app.models import Profile


# Represents an offer with user, title, image, and pricing info.
class Offer(models.Model):
    user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to="offer-img/",
                             max_length=255, blank=True)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    min_price = models.IntegerField()
    min_delivery_time = models.IntegerField()

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        ordering = ["user"]

    def __str__(self):
        return self.title


# Stores features that can be linked to offers.
class Feature(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Feature"
        verbose_name_plural = "Features"
        ordering = ["title"]

    def __str__(self):
        return self.title


# Details for specific offers, including features and pricing.
class OfferDetail(models.Model):
    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name="details")
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.IntegerField()
    features = models.ManyToManyField(Feature)
    offer_type = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Detail"
        verbose_name_plural = "Details"
        ordering = ["title"]

    def __str__(self):
        return self.title

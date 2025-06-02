from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from user_auth_app.models import Profile


class Review(models.Model):
    business_user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="reviewed_user")
    reviewer = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="reviewers")
    rating = models.IntegerField(default=1, validators=[
                                 MaxValueValidator(5), MinValueValidator(1)])
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["pk"]

    def __str__(self):
        return self.description

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Choices for profile type: either business or customer.
TYPE_CHOICES = (
    ("business", "Business"),
    ("customer", "Customer")
)


# Model representing a file related to a profile (e.g. profile image).
class ProfileFile(models.Model):
    file = models.FileField(upload_to="profile-img/", max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"
        ordering = ["file"]
    
    def __str__(self):
        return self.file


# Model representing a user profile, linked to a user and optionally to a file.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles")
    created_at = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=255, blank=True, default="")
    tel = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, default="")
    working_hours = models.CharField(max_length=255, blank=True, default="")
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    file = models.ForeignKey(ProfileFile, on_delete=models.CASCADE, null=True, blank=True, related_name="profiles")
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ["user"]
    
    def __str__(self):
        return self.user.username
    

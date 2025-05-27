from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

TYPE_CHOICES = (
    ("business", "Business"),
    ("customer", "Customer")
)

class ProfileFile(models.Model):
    file = models.FileField(upload_to="profile-img/", max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles")
    created_at = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=255)
    tel = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    working_hours = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    file = models.ForeignKey(ProfileFile, on_delete=models.CASCADE, null=True, blank=True, related_name="profiles")
    
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ["user"]
    
    def __str__(self):
        return self.user.username
    

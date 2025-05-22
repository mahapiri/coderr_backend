from django.contrib.auth.models import User
from django.db import models

TYPE_CHOICES = (
    ("business", "Business"),
    ("customer", "Customer")
)

class Profile(models.Model):
    #pk, username, first_name, last_name, email, created_at
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles")
    file = models.FileField(upload_to="static/img/profile-img/", max_length=255, blank=True)
    # uploaded_at = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    tel = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    working_hours = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ["user"]
    
    def __str__(self):
        return self.user.username
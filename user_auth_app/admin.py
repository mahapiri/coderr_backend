from django.contrib import admin

from user_auth_app.models import Profile, ProfileFile


# Register the Profile model in the Django admin site.
admin.site.register(Profile)

# Register the ProfileFile model in the Django admin site.
admin.site.register(ProfileFile)
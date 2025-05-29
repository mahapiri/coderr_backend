from django.contrib import admin

from user_auth_app.models import Profile, ProfileFile

# Register your models here.
admin.site.register(Profile)
admin.site.register(ProfileFile)
from django.contrib import admin

from user_auth_app.models import Profile, ProfileFile


admin.site.register(Profile)
admin.site.register(ProfileFile)
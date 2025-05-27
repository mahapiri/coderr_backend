from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied

from user_auth_app.models import Profile


class ProfileOwnerPermissions(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        is_owner = obj.user == user
        if not is_owner:
            return False
        return True

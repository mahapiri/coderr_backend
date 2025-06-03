from rest_framework import permissions


class ProfileOwnerPermissions(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        is_owner = obj.user == user
        if not is_owner:
            return False
        return True

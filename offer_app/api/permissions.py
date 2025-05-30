from rest_framework.permissions import BasePermission


class IsBusinessPermission(BasePermission):
    def has_permission(self, request, view):
        try:
            profile = request.user.profiles.first()
            return profile is not None and profile.type == "business"
        except Exception:
            return False
        
class IsOfferOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user.user == request.user
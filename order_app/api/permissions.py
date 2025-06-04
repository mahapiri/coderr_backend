from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission

from user_auth_app.models import Profile


# Permission class that allows only users with a 'customer' profile type.
class IsCustomerUser(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        try:
            customer_profile = Profile.objects.get(user=user)
            if customer_profile.type != "customer":
                return False
            return True
        except Profile.DoesNotExist:
            raise NotFound("Profile was not found!")
        

# Permission class that allows only users with a 'business' profile type.
class IsBusinessUser(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        try:
            business_profile = Profile.objects.get(user=user)
            if business_profile.type != "business":
                return False
            return True
        except Profile.DoesNotExist:
            raise NotFound("Profile was not found!")

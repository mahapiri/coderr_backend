from rest_framework.permissions import BasePermission


# Permission class that allows access only if the user is the owner of the review.
class IsReviewOwner(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        return obj.reviewer.user == request.user

from django.core.serializers import serialize
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from review_app.api.permissions import IsReviewOwner
from review_app.api.serializers import ReviewSerializer
from review_app.models import Review
from user_auth_app.models import Profile


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        business_user_id = params.get("business_user_id")
        reviewer_id = params.get("reviewer_id")
        ordering = params.get("ordering")

        if not any([business_user_id, reviewer_id, ordering]):
            return queryset

        if business_user_id is not None:
            queryset = queryset.filter(business_user__id=business_user_id)
        if reviewer_id is not None:
            queryset = queryset.filter(reviewer__id=reviewer_id)
        if ordering in ["updated:_at", "rating"]:
            queryset = queryset.order_by(ordering)
        return queryset

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated]
        elif self.action in ["partial_update", "update"]:
            permission_classes = [IsAuthenticated, IsReviewOwner]
        elif self.action in ["destroy"]:
            permission_classes = [IsAuthenticated, IsReviewOwner]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        data = request.data
        business_user_id = data.get("business_user")
        description = data.get("description")
        rating = data.get("rating")
        if not business_user_id:
            return Response({"error": "No business profile was provided!"}, status=status.HTTP_400_BAD_REQUEST)

        if not description:
            return Response({"error": "No description was provided!"}, status=status.HTTP_400_BAD_REQUEST)

        if not rating:
            return Response({"error": "No rating was provided!"}, status=status.HTTP_400_BAD_REQUEST)

        reviewer = request.user.profiles.filter(type="customer").first()
        if not reviewer:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            business_user = Profile.objects.get(pk=business_user_id, type="business")
        except Profile.DoesNotExist:
            return Response({"error": "Business profile was not found"}, status=status.HTTP_404_NOT_FOUND)

        if Review.objects.filter(business_user=business_user, reviewer=reviewer).exists():
            return Response({"error": "Forbidden. You have already an existing review"}, status=status.HTTP_403_FORBIDDEN)
        try:
            serializer = self.get_serializer(
                data={"business_user": business_user.pk, "reviewer": reviewer.id, "rating": rating, "description": description})
            serializer.is_valid(raise_exception=True)
            review = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response({"error": "An internal server error occurred!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        review = self.get_object()
        rating = request.data.get("rating")
        description = request.data.get("description")

        if rating is None or description is None:
            return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            review.rating = rating
            review.description = description
            review.save()
            serializer = self.get_serializer(review)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "An internal server error occurred!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        self.perform_destroy(review)
        return Response(status=status.HTTP_204_NO_CONTENT)
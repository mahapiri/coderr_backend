from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from user_auth_app.models import Profile
from review_app.models import Review
from review_app.api.serializers import ReviewSerializer
from review_app.api.permissions import IsReviewOwner


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        business_user_id = params.get("business_user_id")
        reviewer_id = params.get("reviewer_id")
        ordering = params.get("ordering")
        if business_user_id:
            queryset = queryset.filter(business_user__id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer__id=reviewer_id)
        if ordering in ["updated_at", "rating"]:
            queryset = queryset.order_by(ordering)
        return queryset

    def get_permissions(self):
        if self.action in ["partial_update", "update", "destroy"]:
            permission_classes = [IsAuthenticated, IsReviewOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        data = request.data
        business_user_id = data.get("business_user")
        description = data.get("description")
        rating = data.get("rating")
        try:
            self.is_create_data_valid(business_user_id, description, rating)
            reviewer, business_user = self.is_reviewer_already_exists(
                request, business_user_id)
            serializer = self.get_serializer(
                data={"business_user": business_user.pk, "reviewer": reviewer.id, "rating": rating, "description": description})
            serializer.is_valid(raise_exception=True)
            review = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Profile.DoesNotExist:
            return Response({"error": "Business profile was not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:
            return Response({"error": "Invalid request data!"}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied:
            return Response({"error": "Forbidden. You have already an existing review"}, status=status.HTTP_403_FORBIDDEN)
        except NotAuthenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception:
            return Response({"error": "An internal server error occurred!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        review = self.get_object()
        rating = request.data.get("rating")
        description = request.data.get("description")
        try:
            self.is_patch_data_valid(rating, description)
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

    def is_create_data_valid(self, business_user_id, description, rating):
        if business_user_id is None or description is None or rating is None:
            raise ValidationError()

    def is_reviewer_already_exists(self, request, business_user_id):
        reviewer = request.user.profiles.filter(type="customer").first()
        if not reviewer:
            raise NotAuthenticated()
        business_user = Profile.objects.get(
            pk=business_user_id, type="business")
        if Review.objects.filter(business_user=business_user, reviewer=reviewer).exists():
            raise PermissionDenied()
        return reviewer, business_user

    def is_patch_data_valid(self, rating, description):
        if rating is None or description is None:
            raise ValidationError()

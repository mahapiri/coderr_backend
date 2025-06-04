from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from order_app.api.permissions import IsCustomerUser
from user_auth_app.models import Profile
from review_app.models import Review
from review_app.api.serializers import ReviewSerializer
from review_app.api.permissions import IsReviewOwner


# ViewSet for handling CRUD operations on reviews.
class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    # Filters queryset based on query parameters.
    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        queryset = self.get_filter_params(queryset, params)
        return queryset

    # Returns appropriate permissions for each action.
    def get_permissions(self):
        if self.action in ["partial_update", "update", "destroy"]:
            permission_classes = [IsAuthenticated, IsReviewOwner]
        elif self.action == "create":
            permission_classes = [IsAuthenticated, IsCustomerUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @extend_schema(
        summary="List all reviews",
        description="Returns a list of all reviews. You can filter by business_user_id, reviewer_id or order by updated_at/rating.",
        tags=["Review"],
        responses={
            200: ReviewSerializer(many=True),
        }
    )
    # Lists all reviews with optional filtering.
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create a new review",
        description="Creates a new review for a specific business user by a customer. Only one review per customer/business pair is allowed.",
        tags=["Review"],
        responses={
            201: ReviewSerializer,
            400: OpenApiResponse(description="Invalid request data!"),
            401: OpenApiResponse(description="Unauthorized. You must be authenticated and have a customer profile."),
            403: OpenApiResponse(description="Forbidden. You have already an existing review"),
            404: OpenApiResponse(description="Business profile was not found"),
            500: OpenApiResponse(description="An internal server error occurred!"),
        }
    )
    # Creates a new review for a business user.
    def create(self, request, *args, **kwargs):
        data = request.data
        business_user_id = data.get("business_user")
        rating = data.get("rating")
        description = data.get("description")
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
            return Response({"details": "Business profile was not found"}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:
            return Response({"details": "Invalid request data!"}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied:
            return Response({"details": "Forbidden. You have already an existing review"}, status=status.HTTP_403_FORBIDDEN)
        except NotAuthenticated:
            return Response({"details": "Unauthorized. You must be authenticated and have a customer profile."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception:
            return Response({"details": "An internal server error occurred!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Update a review",
        description="Partially updates an existing review (rating and description). Only the review owner can update.",
        tags=["Review"],
        responses={
            200: ReviewSerializer,
            400: OpenApiResponse(description="Invalid request data!"),
            500: OpenApiResponse(description="An internal server error occurred!"),
        }
    )
    # Partially updates a review (only by the review owner).
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
        except ValidationError:
            return Response({"details": "Invalid request data!"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"details": "An internal server error occurred!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Delete a review",
        description="Deletes a review. Only the review owner can delete.",
        tags=["Review"],
        responses={
            204: OpenApiResponse(description="Review deleted"),
            500: OpenApiResponse(description="An internal server error occurred!"),
        }
    )
    # Deletes a review (only by the review owner).
    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        self.perform_destroy(review)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Helper method to filter queryset with query parameters.
    def get_filter_params(self, queryset, params):
        business_user_id = params.get("business_user_id")
        reviewer_id = params.get("reviewer_id")
        ordering = params.get("ordering")
        if business_user_id:
            queryset = queryset.filter(business_user__id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer__id=reviewer_id)
        if ordering in ["updated_at", "rating", "-updated_at", "-rating"]:
            queryset = queryset.order_by(ordering)
        return queryset

    # Validates data for review creation.
    def is_create_data_valid(self, business_user_id, description, rating):
        if business_user_id is None or description is None or rating is None:
            raise ValidationError()

    # Checks if reviewer already exists for the given business user.
    def is_reviewer_already_exists(self, request, business_user_id):
        reviewer = request.user.profiles.filter(type="customer").first()
        if not reviewer:
            raise NotAuthenticated()
        business_user = Profile.objects.get(
            pk=business_user_id, type="business")
        if Review.objects.filter(business_user=business_user, reviewer=reviewer).exists():
            raise PermissionDenied()
        return reviewer, business_user

    # Validates data for review update.
    def is_patch_data_valid(self, rating, description):
        if rating is None or description is None:
            raise ValidationError()

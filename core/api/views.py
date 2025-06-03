from django.db.models import Avg
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offer_app.models import Offer
from user_auth_app.models import Profile
from review_app.models import Review
from core.api.serializers import BaseInfoSerializer


class BaseInfoViewSet(APIView):
    """
    API endpoint that provides general statistics about the platform.
    Returns the total number of reviews, the average rating, the number of business profiles,
    and the total number of offers.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Get platform statistics",
        description=(
            "Returns aggregated information about the platform, including:\n"
            "- The total number of reviews (`review_count`)\n"
            "- The average review rating (`average_rating`)\n"
            "- The number of business profiles (`business_profile_count`)\n"
            "- The total number of offers (`offer_count`)\n"
            "\n"
            "This endpoint is publicly accessible and requires no authentication."
        ),
        tags=["BaseInfo"],
        responses={
            200: BaseInfoSerializer,
            500: OpenApiResponse(description="An internal server error occurred"),
        },
    )
    def get(self, request, *args, **kwargs):
        try:
            review_count = Review.objects.all().count()
            average_rating_dict = Review.objects.aggregate(avg_rating=Avg("rating"))
            average_rating = average_rating_dict["avg_rating"] or 0
            business_profile_count = Profile.objects.filter(type="business").count()
            offer_count = Offer.objects.all().count()
            serializer = BaseInfoSerializer({
                "review_count": review_count,
                "average_rating": average_rating,
                "business_profile_count": business_profile_count,
                "offer_count": offer_count
            })
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"details": "An Internal server error occured!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

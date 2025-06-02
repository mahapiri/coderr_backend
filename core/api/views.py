

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.serializers import BaseInfoSerializer
from review_app.models import Review


class BaseInfoViewSet(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            review_count = Review.objects.all().count()
            print(review_count)
            average_rating = "10"
            business_profile_count = "10"
            offer_count = "10"
            serializer = BaseInfoSerializer({
                "review_count": review_count,
                "average_rating": average_rating,
                "business_profile_count": business_profile_count,
                "offer_count": offer_count
            })
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Internal server was occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

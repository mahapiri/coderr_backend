from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from review_app.api.serializers import ReviewSerializer
from review_app.models import Review


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

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
        
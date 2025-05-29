from django.http import QueryDict
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from offer_app.api.pagination import OfferPagination
from offer_app.api.serializers import OfferGetSerializer
from offer_app.models import Offer


class OfferViewSet(ModelViewSet):
    pagination_class = OfferPagination
    serializer_class = OfferGetSerializer
    permission_classes = [AllowAny]
    queryset = Offer.objects.all()
    # required_param_fields = ("creator_id")

    def retrieve(self, request, *args, **kwargs):
        creator_id = request.query_params.get("creator_id")
        print(creator_id)
        return super().retrieve(request, *args, **kwargs)
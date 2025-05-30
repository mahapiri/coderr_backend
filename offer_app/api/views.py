from django.core.serializers import serialize
from rest_framework import filters, status
from rest_framework.decorators import permission_classes
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from offer_app.admin import Feature, OfferDetail
from offer_app.api.pagination import OfferPagination
from offer_app.api.permissions import IsBusinessPermission, IsOfferOwner
from offer_app.api.serializers import OfferCreateSerializer, OfferDetailResponseSerializer, OfferResponseSerializer, OfferSerializer, OfferUpdatedResponseSerializer
from offer_app.models import Offer


class InvalidQueryParameter(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "At least one valid request parameter must be passed."
    default_code = "invalid_query_parameter"


class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all().select_related(
        "user").prefetch_related("details")
    pagination_class = OfferPagination
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["updated_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OfferResponseSerializer
        elif self.action == "list":
            return OfferSerializer
        elif self.action == "create":
            return OfferCreateSerializer
        return OfferResponseSerializer

    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsAuthenticated, IsOfferOwner]
        elif self.action == "retrieve":
            permission_classes = [IsAuthenticated]
        elif self.action == "list":
            permission_classes = [AllowAny]
        elif self.action == "create":
            permission_classes = [IsAuthenticated, IsBusinessPermission]
        elif self.action in ["partial_update", "update"]:
            permission_classes = [IsAuthenticated, IsOfferOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params

        if self.action in ["partial_update", "update", "retrieve", "destroy"]:
            return queryset

        creator_id = params.get("creator_id")
        min_price = params.get("min_price")
        max_delivery_time = params.get("max_delivery_time")
        search = params.get("search")
        ordering = params.get("ordering")

        if not any([creator_id, min_price, max_delivery_time, search, ordering]):
            raise InvalidQueryParameter()

        if creator_id is not None:
            queryset = queryset.filter(user__id=creator_id)
        if min_price is not None:
            queryset = queryset.filter(min_price__gte=min_price)
        if max_delivery_time is not None:
            queryset = queryset.filter(
                min_delivery_time__lte=max_delivery_time)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data

        profile = request.user.profiles.first()
        if not profile or profile.type != "business":
            return Response({"error": "Only Business Profile can create an offer!"}, status=status.HTTP_403_FORBIDDEN)

        details = data.get("details", [])
        if not isinstance(details, list) or len(details) != 3:
            return Response({"error": "An offer should have exactly 3 details!"}, status=status.HTTP_400_BAD_REQUEST)

        offer = Offer.objects.create(
            user=profile,
            title=data.get('title'),
            image=data.get('image'),
            description=data.get('description'),
            min_price=min(d['price'] for d in details),
            min_delivery_time=min(d['delivery_time_in_days'] for d in details)
        )

        for detail in details:
            features = detail.pop('features', [])
            offer_detail = OfferDetail.objects.create(
                offer=offer,
                title=detail.get('title'),
                revisions=detail.get('revisions'),
                delivery_time_in_days=detail.get('delivery_time_in_days'),
                price=detail.get('price'),
                offer_type=detail.get('offer_type'),
            )
            feature_objs = []
            for feature_title in features:
                feature_obj, _ = Feature.objects.get_or_create(
                    title=feature_title)
                feature_objs.append(feature_obj)
            offer_detail.features.set(feature_objs)

        serializer = OfferResponseSerializer(offer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        offer = self.get_object()
        data = request.data
        details_data = data.pop("details", None)

        for field, value in data.items():
            if value is not None:
                setattr(offer, field, value)
        offer.save()

        if details_data is not None:
            for detail_update in details_data:
                required_fields = [
                    "title", "revisions", "delivery_time_in_days", "price", "features", "offer_type"]
                missing = [
                    f for f in required_fields if f not in detail_update]
                if missing:
                    return Response(
                        {"error": "Incomplete details"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                allowed_set = set(required_fields)
                detail_keys = set(detail_update.keys())
                extra = detail_keys - allowed_set
                if extra:
                    return Response(
                        {"error": "Invalid request data"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                offer_type = detail_update.get("offer_type")
                try:
                    detail_obj = offer.details.get(offer_type=offer_type)
                except OfferDetail.DoesNotExist:
                    return Response({"error": "detail was not found"}, status=status.HTTP_400_BAD_REQUEST)

                for field in ["title", "revisions", "delivery_time_in_days", "price", "offer_type"]:
                    if field in detail_update and detail_update[field] is not None:
                        setattr(detail_obj, field, detail_update[field])
                detail_obj.save()

                if "features" in detail_update and detail_update["features"] is not None:
                    feature_titles = detail_update["features"]
                    feature_objs = []
                    for title in feature_titles:
                        feat_obj, _ = Feature.objects.get_or_create(
                            title=title)
                        feature_objs.append(feat_obj)
                    detail_obj.features.set(feature_objs)

        all_details = offer.details.all()
        if all_details:
            offer.min_price = min([d.price for d in all_details])
            offer.min_delivery_time = min(
                [d.delivery_time_in_days for d in all_details])
            offer.save()

        offer.refresh_from_db()

        serializer = OfferUpdatedResponseSerializer(
            offer, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        offer = self.get_object()
        self.perform_destroy(offer)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class OfferDetailView(ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailResponseSerializer
    permission_classes = [IsAuthenticated]

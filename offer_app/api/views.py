from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import filters, status
from rest_framework.exceptions import APIException, NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from offer_app.models import Offer
from offer_app.admin import Feature, OfferDetail
from offer_app.api.pagination import OfferPagination
from offer_app.api.permissions import IsBusinessPermission, IsOfferOwner
from offer_app.api.serializers import OfferCreateSerializer, OfferDetailResponseSerializer, OfferResponseSerializer, OfferRetrieveSerializer, OfferSerializer, OfferUpdatedResponseSerializer


# ViewSet for handling all Offer CRUD operations and filtering.
class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all().select_related(
        "user").prefetch_related("details")
    pagination_class = OfferPagination
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    ordering = ["updated_at"]

    # Returns the serializer class based on the current action.
    def get_serializer_class(self):
        if self.action == "retrieve":
            return OfferRetrieveSerializer
        elif self.action == "list":
            return OfferSerializer
        elif self.action == "create":
            return OfferCreateSerializer
        return OfferResponseSerializer
    
    # Returns the correct permission classes depending on action.
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

    # Gets and filters the queryset based on query parameters for listing.
    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        if self.action in ["partial_update", "update", "retrieve", "destroy"]:
            return queryset
        queryset = self.get_params_to_filter(params, queryset)
        return queryset

    @extend_schema(
        summary="List all offers",
        description="Returns a paginated list of all offers. You can filter offers by creator, minimum price, maximum delivery time, or search in title/description.",
        tags=["Offer"],
        responses={
            200: OfferSerializer(many=True),
            400: OpenApiResponse(description="At least one valid request parameter must be passed."),
        }
    )
    # Returns a paginated list of all offers.
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve offer details",
        description="Returns the details of a single offer by its ID.",
        tags=["Offer"],
        responses={
            200: OfferRetrieveSerializer,
            404: OpenApiResponse(description="Offer not found."),
        }
    )
    # Retrieves the details of a single offer by its ID.
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new offer",
        description="Creates a new offer with exactly three details. Only business profiles can create offers.",
        tags=["Offer"],
        responses={
            201: OfferResponseSerializer,
            400: OpenApiResponse(description="An offer should have exactly 3 details!"),
            403: OpenApiResponse(description="Only Business Profile can create an offer!"),
            500: OpenApiResponse(description="Internal Server Error"),
        }
    )
    # Creates a new offer with details. Only business profiles are allowed.
    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            profile = self.is_valid_business_profile(request)
            offer, details = self.create_offer(data, profile)
            self.create_details_features(details, offer)
            serializer = OfferResponseSerializer(offer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except PermissionDenied:
            return Response({"details": "Only Business Profile can create an offer!"}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError:
            return Response({"details": "An offer should have exactly 3 details!"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"details": "An Internal server error occured!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Partially update an offer",
        description="Partially updates an offer and its details. Only the offer owner can update.",
        tags=["Offer"],
        responses={
            200: OfferUpdatedResponseSerializer,
            400: OpenApiResponse(description="Invalid or incomplete details data."),
            404: OpenApiResponse(description="Detail was not found."),
        }
    )
    # Partially updates an offer and its details.
    def partial_update(self, request, *args, **kwargs):
        offer = self.get_object()
        data = request.data
        details_data = data.pop("details", None)
        try:
            self.update_offer_fields(offer, data)
            if details_data is not None:
                self.update_offer_details(offer, details_data)
            self.update_offer_min_values(offer)
            offer.refresh_from_db()
            serializer = OfferUpdatedResponseSerializer(
                offer, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotFound:
            return Response({"details": "detail was not found"}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete an offer",
        description="Deletes an offer. Only the offer owner can delete.",
        tags=["Offer"],
        responses={
            204: OpenApiResponse(description="Offer successfully deleted."),
            500: OpenApiResponse(description="Internal Server error occurred!"),
        }
    )
    # Deletes an offer. Only the owner can delete.
    def destroy(self, request, *args, **kwargs):
        offer = self.get_object()
        self.perform_destroy(offer)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Updates the fields of an offer with provided data.
    def update_offer_fields(self, offer, data):
        for field, value in data.items():
            if value is not None:
                setattr(offer, field, value)
        offer.save()

    # Updates the details for an offer with validation.
    def update_offer_details(self, offer, details_data):
        for detail_update in details_data:
            self.validate_detail_update(detail_update)
            self.update_single_detail(offer, detail_update)

    # Validates that all required fields are present in the detail update.
    def validate_detail_update(self, detail_update):
        required_fields = [
            "title", "revisions", "delivery_time_in_days", "price", "features", "offer_type"
        ]
        missing = [f for f in required_fields if f not in detail_update]
        if missing:
            raise ValidationError("Incomplete details")
        allowed_set = set(required_fields)
        detail_keys = set(detail_update.keys())
        extra = detail_keys - allowed_set
        if extra:
            raise ValidationError("Invalid request data")

    # Updates a single offer detail object with new values.
    def update_single_detail(self, offer, detail_update):
        offer_type = detail_update.get("offer_type")
        try:
            detail_obj = offer.details.get(offer_type=offer_type)
        except OfferDetail.DoesNotExist:
            raise NotFound()
        for field in ["title", "revisions", "delivery_time_in_days", "price", "offer_type"]:
            if field in detail_update and detail_update[field] is not None:
                setattr(detail_obj, field, detail_update[field])
        detail_obj.save()
        self.update_detail_features(detail_obj, detail_update.get("features"))

    # Updates the features for a detail object.
    def update_detail_features(self, detail_obj, feature_titles):
        if feature_titles is not None:
            feature_objs = [Feature.objects.get_or_create(
                title=title)[0] for title in feature_titles]
            detail_obj.features.set(feature_objs)

    # Recalculates min price and delivery time for the offer.
    def update_offer_min_values(self, offer):
        all_details = offer.details.all()
        if all_details:
            offer.min_price = min([d.price for d in all_details])
            offer.min_delivery_time = min(
                [d.delivery_time_in_days for d in all_details])
            offer.save()

    # Filters queryset by URL parameters if present.
    def get_params_to_filter(self, params, queryset):
        creator_id = params.get("creator_id")
        min_price = params.get("min_price")
        max_delivery_time = params.get("max_delivery_time")

        if creator_id:
            queryset = queryset.filter(user__id=creator_id)
        if min_price:
            try:
                queryset = queryset.filter(min_price__gte=float(min_price))
            except ValueError:
                raise ValidationError({"min_price": "Must be a number"})
        if max_delivery_time:
            try:
                queryset = queryset.filter(min_delivery_time__lte=int(max_delivery_time))
            except ValueError:
                raise ValidationError({"max_delivery_time": "Must be an integer"})
        return queryset

    # Checks if the user profile is a valid business type.
    def is_valid_business_profile(self, request):
        profile = request.user.profiles.first()
        if not profile or profile.type != "business":
            raise PermissionDenied()
        return profile

    # Creates a new offer and returns the offer and details.
    def create_offer(self, data, profile):
        details = data.get("details", [])
        if not isinstance(details, list) or len(details) != 3:
            raise ValidationError()

        offer = Offer.objects.create(
            user=profile,
            title=data.get('title'),
            image=data.get('image'),
            description=data.get('description'),
            min_price=min(d['price'] for d in details),
            min_delivery_time=min(d['delivery_time_in_days'] for d in details)
        )
        return offer, details

    # Creates offer details and links features to them.
    def create_details_features(self, details, offer):
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


# Read-only view for listing and retrieving offer details.
class OfferDetailView(ReadOnlyModelViewSet):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailResponseSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List all offer details",
        description="Returns a list of all offer details.",
        tags=["Offer"],
        responses={
            200: OfferDetailResponseSerializer(many=True)
        }
    )
    # Returns a list of all offer details.
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve offer detail",
        description="Returns the details of a single offer detail by its ID.",
        tags=["Offer"],
        responses={
            200: OfferDetailResponseSerializer,
            404: OpenApiResponse(description="Offer detail not found."),
        }
    )
    # Retrieves the details of a single offer detail by its ID.
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

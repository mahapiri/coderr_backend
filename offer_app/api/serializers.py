from rest_framework import serializers

from offer_app.models import Offer, OfferDetail
from user_auth_app.models import Profile


class UserDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "username"]

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_username(self, obj):
        return obj.user.username


class OfferDetailSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, read_only=True)
    user_details = UserDetailSerializer(source="user", read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id", "user", "title", "image", "description",
            "created_at", "updated_at", "details",
            "min_price", "min_delivery_time", "user_details"
        ]

class OfferDetailResponseSerializer(serializers.ModelSerializer):
    features = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = [
            "id", "title", "revisions", "delivery_time_in_days", "price", "features", "offer_type"
        ]

    def get_features(self, obj):
        return [f.title for f in obj.features.all()]
    

class OfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = [
            "id", "title", "image", "description", "details"
        ]
        extra_kwargs = {
            "details": {"required": True}
        }

class OfferResponseSerializer(serializers.ModelSerializer):
    details = OfferDetailResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id", "title", "image", "description", "details"
        ]

class OfferDetailListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ("id", "url")

    def get_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"/api/offerdetails/{obj.id}/")
        return f"/api/offerdetails/{obj.id}/"

class OfferUpdatedResponseSerializer(serializers.ModelSerializer):
    details = OfferDetailResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = (
            "id", "title", "image", "description", "details",
        )

class OfferRetrieveSerializer(serializers.ModelSerializer):
    details = OfferDetailListSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id", "user", "title", "image", "description",
            "created_at", "updated_at", "details",
            "min_price", "min_delivery_time"
        ]
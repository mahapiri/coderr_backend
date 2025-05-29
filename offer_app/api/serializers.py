from rest_framework import serializers

from offer_app.models import Offer


class OfferGetSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details"
        ]

    def get_details(self, obj):
        id = obj.id
        return {
            "id": id,
            "url": f"/offerdetails/{id}/"
        }


    def get_user_details(self, obj):
        user = obj.user.user
        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username
        }
    




class OfferSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer
        fields = [
            "title",
            "image",
            "description",
            "details"
        ]

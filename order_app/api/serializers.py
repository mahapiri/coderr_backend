from rest_framework import serializers

from order_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="offer_detail.title", read_only=True)
    revisions = serializers.IntegerField(source="offer_detail.revisions", read_only=True)
    delivery_time_in_days = serializers.IntegerField(source="offer_detail.delivery_time_in_days", read_only=True)
    price = serializers.IntegerField(source="offer_detail.price", read_only=True)
    features = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="title", source="offer_detail.features"
    )
    offer_type = serializers.CharField(source="offer_detail.offer_type", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at"
        ]


class OrderCountSerializer(serializers.Serializer):
    order_count = serializers.IntegerField()


class CompletedOrderSerializer(serializers.Serializer):
    completed_order_count = serializers.IntegerField()
from rest_framework import serializers


# Serializer for basic info: reviews, average rating, business profiles, and offers.
class BaseInfoSerializer(serializers.Serializer):
    review_count = serializers.IntegerField()
    average_rating = serializers.DecimalField(decimal_places=1, max_digits=3)
    business_profile_count = serializers.IntegerField()
    offer_count = serializers.IntegerField()


from rest_framework import serializers


class BaseInfoSerializer(serializers.Serializer):
    review_count = serializers.IntegerField()
    average_rating = serializers.IntegerField()
    business_profile_count = serializers.IntegerField()
    offer_count = serializers.IntegerField()
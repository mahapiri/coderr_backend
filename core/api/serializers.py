from rest_framework import serializers

class BaseInfoSerializer(serializers.Serializer):
    review_count = serializers.IntegerField()
    average_rating = serializers.DecimalField(decimal_places=1, max_digits=2)
    business_profile_count = serializers.IntegerField()
    offer_count = serializers.IntegerField()
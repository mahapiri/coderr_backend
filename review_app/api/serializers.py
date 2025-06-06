from rest_framework import serializers

from review_app.models import Review


# Serializer for the Review model.
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "business_user", "reviewer", "rating", "description", "created_at", "updated_at"]
        

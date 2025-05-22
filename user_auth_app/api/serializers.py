from django.contrib.auth.models import User
from rest_framework import serializers

from user_auth_app.models import TYPE_CHOICES


class ProfilRegistrationSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True, min_length=8)
    type = serializers.ChoiceField(choices=TYPE_CHOICES)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError({"email": "This email address already exist!"})
        return value
    
    def validate(self, data):
        if data.get("password") != data.get("repeated_password"):
            raise serializers.ValidationError({"passwords": "The passwords do not match!"})
        data.pop("repeated_password")
        return data
    

class ProfilResponseSerializer(serializers.Serializer):

    token = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    user_id = serializers.IntegerField()
    

class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)

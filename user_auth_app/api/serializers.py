from django.contrib.auth.models import User
from rest_framework import serializers

from user_auth_app.models import TYPE_CHOICES, Profile


class ProfilRegistrationSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True, min_length=8)
    type = serializers.ChoiceField(choices=TYPE_CHOICES)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {"email": "This email address already exist!"})
        return value

    def validate(self, data):
        if data.get("password") != data.get("repeated_password"):
            raise serializers.ValidationError(
                {"passwords": "The passwords do not match!"})
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


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        verbose_name = ["Profile"]
        verbose_name_plural = ["Profiles"]
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at"]

    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return None

    def get_first_name(self, obj):
        if obj.user:
            return obj.user.first_name
        return None

    def get_last_name(self, obj):
        if obj.user:
            return obj.user.last_name
        return None

    def get_email(self, obj):
        if obj.user:
            return obj.user.email
        return None

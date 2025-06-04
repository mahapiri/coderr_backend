from django.contrib.auth.models import User

from rest_framework import serializers

from user_auth_app.models import TYPE_CHOICES, Profile


# Serializer for user registration, including password confirmation and type.
class ProfilRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True, min_length=8)
    type = serializers.ChoiceField(choices=TYPE_CHOICES)

    # Validate that the email is unique.
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {"email": "This email address already exist!"})
        return value

    # Validate that the passwords match, remove repeated_password from the data.
    def validate(self, data):
        if data.get("password") != data.get("repeated_password"):
            raise serializers.ValidationError(
                {"passwords": "The passwords do not match!"})
        data.pop("repeated_password")
        return data


# Serializer for returning authentication responses (e.g., token).
class ProfilResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    user_id = serializers.IntegerField()


# Serializer for user login.
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)


# Serializer for the Profile model, including related user fields and custom fields.
class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

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

    # Get the username from the related user.
    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return None

    # Get the first name from the related user.
    def get_first_name(self, obj):
        if obj.user:
            return obj.user.first_name
        return None

    # Get the last name from the related user.
    def get_last_name(self, obj):
        if obj.user:
            return obj.user.last_name
        return None

    # Get the user's file if it exists.
    def get_file(self, obj):
        if obj.file:
            return obj.file.file

    # Get the user's email from the related user.
    def get_email(self, obj):
        if obj.user:
            return obj.user.email
        return None

    # Format the created_at date.
    def get_created_at(self, obj):
        if obj.created_at:
            formatted_date = obj.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            return formatted_date
        return None


# Serializer for business profiles, with selected fields.    
class BusinessSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()

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
            "type"]

    # Get the username from the related user.
    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return None

    # Get the first name from the related user.
    def get_first_name(self, obj):
        if obj.user:
            return obj.user.first_name
        return None

    # Get the last name from the related user.
    def get_last_name(self, obj):
        if obj.user:
            return obj.user.last_name
        return None

    # Get the user's file if it exists.
    def get_file(self, obj):
        if obj.file:
            return obj.file
        return None
    

# Serializer for customer profiles, with selected fields.
class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    uploaded_at = serializers.SerializerMethodField()

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
            "uploaded_at",
            "type"]

    # Get the username from the related user.
    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return None

    # Get the first name from the related user.
    def get_first_name(self, obj):
        if obj.user:
            return obj.user.first_name
        return None

    # Get the last name from the related user.
    def get_last_name(self, obj):
        if obj.user:
            return obj.user.last_name
        return None

    # Get the user's file if it exists.
    def get_file(self, obj):
        if obj.file:
            return obj.file
        return None

    # Get the uploaded_at date for the file if it exists.
    def get_uploaded_at(self, obj):
        if obj.file:
            return obj.file.uploaded_at
        return None

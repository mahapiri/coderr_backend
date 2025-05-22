from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from user_auth_app.api.serializers import LoginSerializer, ProfilResponseSerializer, ProfilRegistrationSerializer, ProfileSerializer
from user_auth_app.models import Profile


class ProfilRegistrationView(generics.CreateAPIView):

    serializer_class = ProfilRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            self.validate_serializer(serializer)
            user = self.create_user(serializer.validated_data)
            profile = self.create_profile(user, serializer.validated_data)

            token, created = Token.objects.get_or_create(user=user)
            response_data = self.create_response_data(token, profile, user)
            response_serializer = ProfilResponseSerializer(response_data)
            return Response(response_serializer.data, content_type="application/json", status=status.HTTP_201_CREATED)
        except ValidationError:
            return Response({"error": f"Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "An internal server error occurred!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def validate_serializer(self, serializer):
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

    def create_user(self, validated_data):
        try:
            created_user = User.objects.create_user(
                username=validated_data["username"],
                email=validated_data["email"],
                password=validated_data["password"]
            )
            return created_user
        except Exception:
            raise Exception()

    def create_profile(self, user, validated_data):
        try:
            new_profile = Profile.objects.create(
                user=user,
                type=validated_data["type"]
            )
            return new_profile
        except Exception:
            user.delete()
            raise Exception()

    def create_response_data(self, token, profile, user):
        return {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": profile.id
        }


class ProfilLoginView(generics.GenericAPIView):

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = self.authenticate_user(serializer)
            if user:
                profile = Profile.objects.filter(user=user).first()
                token, created = Token.objects.get_or_create(user=user)
                response_data = self.create_response_data(token, profile, user)
                response_serializer = ProfilResponseSerializer(response_data)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An internal server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def authenticate_user(self, serializer):
        return authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"]
        )

    def create_response_data(self, token, profile, user):
        return {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": profile.id
        }
    
class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]

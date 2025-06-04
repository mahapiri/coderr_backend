from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from user_auth_app.api.permissions import ProfileOwnerPermissions
from user_auth_app.api.serializers import BusinessSerializer, CustomerSerializer, LoginSerializer, ProfilResponseSerializer, ProfilRegistrationSerializer, ProfileSerializer
from user_auth_app.models import Profile


# View for registering a new user and profile.
class ProfilRegistrationView(generics.CreateAPIView):
    serializer_class = ProfilRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register a new user profile",
        description="Creates a new user and profile. Returns an authentication token and basic user info.",
        tags=["Authentication"],
        responses={
            201: ProfilResponseSerializer,
            400: OpenApiResponse(description="Invalid request data"),
            500: OpenApiResponse(description="An internal server error occurred!"),
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            self.validate_serializer(serializer)
            user = self.create_user(serializer.validated_data)
            profile = self.create_profile(user, serializer.validated_data)

            token, _ = Token.objects.get_or_create(user=user)
            response_data = self.create_response_data(token, profile, user)
            response_serializer = ProfilResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError:
            return Response({"details": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"details": "An internal server error occurred!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Validates the serializer data.
    def validate_serializer(self, serializer):
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

    # Creates a new User instance.
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

    # Creates a new Profile instance associated with the user.
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

    # Prepares the response data for registration.
    def create_response_data(self, token, profile, user):
        return {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": profile.id
        }


# View for authenticating a user and returning a token.
class ProfilLoginView(generics.GenericAPIView):

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login and obtain token",
        description="Authenticates a user and returns an authentication token along with user info.",
        tags=["Authentication"],
        responses={
            200: ProfilResponseSerializer,
            400: OpenApiResponse(description="Invalid email or password"),
            500: OpenApiResponse(description="An internal server error occurred!"),
        }
    )
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
            return Response({"details": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"details": f"An internal server error occurred!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Authenticates the user with provided credentials.
    def authenticate_user(self, serializer):
        return authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"]
        )

    # Prepares the response data for login.
    def create_response_data(self, token, profile, user):
        return {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": profile.id
        }


# ViewSet for CRUD operations on profiles.
class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]

    # Returns appropriate permissions for each action.
    def get_permissions(self):
        if self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated, ProfileOwnerPermissions]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    # Retrieves a profile object, raising NotFound if not found.
    def get_object(self):
        try:
            obj = super().get_object()
            return obj
        except (ObjectDoesNotExist, Http404):
            raise NotFound("Profile was not found!")

    @extend_schema(
        summary="Retrieve a profile",
        description="Returns the profile for a given user ID.",
        tags=["Profile"],
        responses={
            200: ProfileSerializer,
            404: OpenApiResponse(description="Profile was not found!"),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update a profile",
        description="Updates profile data. Only the profile owner can update.",
        tags=["Profile"],
        responses={
            200: ProfileSerializer,
            403: OpenApiResponse(description="Forbidden. You should be the owner of this profile!"),
            404: OpenApiResponse(description="Profile was not found!"),
            500: OpenApiResponse(description="An Internal server error occured!"),
        }
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.get("partial", False)
            instance = self.get_object()
            user = instance.user
            data = self.update_fields(request, user)
            serializer = self.get_serializer(instance, data=data, partial=partial, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound:
            return Response({"details": "Profile was not found!"}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({"details": "Forbidden. You should be the owner of this profile!"}, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            return Response({"details": "An Internal server error occured!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Updates user fields if present in the request data.
    def update_fields(self, request, user):
        data = request.data.copy()
        user_fields = ["first_name", "last_name", "email"]
        updated = False
        for field in user_fields:
            if field in data:
                setattr(user, field, data[field])
                updated = True
        if updated:
            user.save()
        return data


# View for listing all business profiles.
class BusinessListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessSerializer
    queryset = Profile.objects.all()

    @extend_schema(
        summary="List all business profiles",
        description="Returns a list of all profiles with type 'business'.",
        tags=["Profile"],
        responses={
            200: BusinessSerializer(many=True),
            500: OpenApiResponse(description="Internal Server error occured!"),
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            data = Profile.objects.filter(type="business")
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"details": "Internal Server error occured!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# View for listing all customer profiles.
class CustomerListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer
    queryset = Profile.objects.all()

    @extend_schema(
        summary="List all customer profiles",
        description="Returns a list of all profiles with type 'customer'.",
        tags=["Profile"],
        responses={
            200: CustomerSerializer(many=True),
            500: OpenApiResponse(description="Internal Server error!"),
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            data = Profile.objects.filter(type="customer")
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"details": "Internal Server error!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

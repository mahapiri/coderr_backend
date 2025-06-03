from django.db import models
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from offer_app.admin import OfferDetail
from order_app.api.permissions import IsBusinessUser, IsCustomerUser
from order_app.api.serializers import CompletedOrderSerializer, OrderCountSerializer, OrderSerializer
from order_app.models import STATUS_CHOICE, Order
from user_auth_app.models import Profile


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            if user.is_staff:
                return Order.objects.all()
            profile = user.profiles.first()
            return Order.objects.filter(
                models.Q(customer_user=profile) | models.Q(business_user=profile)
            ).distinct()
        except Exception:
            return Response({"details": "An Internal server error occured!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == "create":
            permission_classes = [IsAuthenticated, IsCustomerUser]
        elif self.action in ["partial_update", "update"]:
            permission_classes = [IsAuthenticated, IsBusinessUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @extend_schema(
        summary="List orders of the current user",
        description=(
            "Returns all orders where the current authenticated user is either the customer or the business user. "
            "Admins see all orders."
        ),
        tags=["Order"],
        responses={200: OrderSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new order",
        description=(
            "Creates a new order for the authenticated customer. "
            "Requires a valid offer_detail_id in the request data."
        ),
        tags=["Order"],
        responses={
            201: OrderSerializer,
            400: OpenApiResponse(description="Missing or invalid offer_detail_id"),
            401: OpenApiResponse(description="Profile was not found."),
            404: OpenApiResponse(description="Offer not found."),
            500: OpenApiResponse(description="Internal server error")
        }
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            customer_profile = Profile.objects.get(user=user)
            offer_detail_id = int(request.data.get("offer_detail_id"))
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
            business_profile = offer_detail.offer.user
            order = Order.objects.create(
                customer_user=customer_profile,
                business_user=business_profile,
                offer_detail=offer_detail,
                status="in_progress"
            )
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except OfferDetail.DoesNotExist:
            return Response({"details": "Offer not found"}, status=status.HTTP_404_NOT_FOUND)
        except (TypeError, ValueError):
            return Response({"details": "offer_detail_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({"details": "Profile was not found."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception:
            return Response({"details": "An Internal server error occured!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Partially update an order's status",
        description=(
            "Updates the status of an order. Only the business user of the order is allowed to update. "
            "Status must be one of the valid choices."
        ),
        tags=["Order"],
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(description="Invalid request data"),
            403: OpenApiResponse(description="You have no permission"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
    def partial_update(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = Profile.objects.get(user=user)
            order = self.get_object()
            if order.business_user != profile:
                raise PermissionDenied()
            allowed_status = [key for key in STATUS_CHOICE.keys()]
            new_status = request.data.get("status")
            if not new_status or new_status not in allowed_status:
                raise ValidationError()
            order.status = new_status
            order.save()
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"details": "An Internal server error occured!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except PermissionDenied:
            return Response({"details": "You have no permission"}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError:
            return Response({"details": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete an order",
        description="Deletes an order. Only admins are allowed to delete orders.",
        tags=["Order"],
        responses={
            204: OpenApiResponse(description="Order deleted"),
            404: OpenApiResponse(description="Order not found!"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            order = self.get_object()
            self.perform_destroy(order)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response({"details": "Order not found!"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"details": "An Internal server error occured!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get count of in-progress orders for a business user",
        description=(
            "Returns the number of orders with status 'in_progress' for the specified business user."
        ),
        tags=["Order"],
        parameters=[
            OpenApiParameter(
                name="business_user_id",
                description="Primary key of the business user profile",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            200: OrderCountSerializer,
            404: OpenApiResponse(description="No business user was found!"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
    def get(self, request, business_user_id):
        try:
            profile = Profile.objects.get(pk=business_user_id, type="business")
            order_count = Order.objects.filter(business_user=profile, status="in_progress").count()
            serializer = OrderCountSerializer({"order_count": order_count})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"details": "No business user was found!"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"details": "An Internal server error occured!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompletedOrderView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get count of completed orders for a business user",
        description=(
            "Returns the number of orders with status 'completed' for the specified business user."
        ),
        tags=["Order"],
        parameters=[
            OpenApiParameter(
                name="business_user_id",
                description="Primary key of the business user profile",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            ),
        ],
        responses={
            200: CompletedOrderSerializer,
            404: OpenApiResponse(description="No business user was found!"),
            500: OpenApiResponse(description="Internal server error")
        }
    )
    def get(self, request, business_user_id):
        try:
            profile = Profile.objects.get(pk=business_user_id, type="business")
            order_count = Order.objects.filter(business_user=profile, status="completed").count()
            serializer = CompletedOrderSerializer({"completed_order_count": order_count})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({"details": "No business user was found!"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({"details": "An Internal server error occured!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

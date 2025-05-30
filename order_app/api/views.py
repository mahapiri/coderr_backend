from django.db import models
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from offer_app.admin import OfferDetail
from order_app.api.permissions import IsBusinessUser, IsCustomerUser
from order_app.api.serializers import OrderSerializer
from order_app.models import STATUS_CHOICE, Order
from user_auth_app.models import Profile


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        profile = user.profiles.first()
        return Order.objects.filter(
            models.Q(customer_user=profile) | models.Q(business_user=profile)
        ).distinct()
    
    def get_permissions(self):
        if self.action == "destroy":
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == "retrieve":
            permission_classes = [IsAuthenticated]
        elif self.action == "list":
            permission_classes = [IsAuthenticated]
        elif self.action == "create":
            permission_classes = [IsAuthenticated, IsCustomerUser]
        elif self.action in ["partial_update", "update"]:
            permission_classes = [IsAuthenticated, IsBusinessUser]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        user = request.user

        try:
            customer_profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response({"error": "Profile was not found."}, status=status.HTTP_401_UNAUTHORIZED)
        
        offer_detail_id = request.data.get("offer_detail_id")
        if not offer_detail_id:
            return Response({"error": "offer_detail_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            return Response({"error": "Offer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        business_profile = offer_detail.offer.user

        order = Order.objects.create(
            customer_user=customer_profile,
            business_user=business_profile,
            offer_detail=offer_detail,
            status="in_progress"
        )

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.get(user=user)

        order = self.get_object()

        if order.business_user != profile:
            return Response({"error": "You have no permission"}, status=status.HTTP_403_FORBIDDEN)
        
        allowed_status = [key for key in STATUS_CHOICE.keys()]
        new_status = request.data.get("status")

        if not new_status or new_status not in allowed_status:
            return Response(
                {"error": "Invalid request data"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = new_status
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        try:
            order = self.get_object()
        except Order.DoesNotExist:
            return Response({"error": "Order not found!"}, status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(order)
        return Response(status=status.HTTP_204_NO_CONTENT)
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Subscriber, SubscriptionPreference, Campaign
from .serializers import (
    SubscribeSerializer, UnsubscribeSerializer, ConfirmSerializer,
    SubscriptionPreferenceSerializer, CampaignSerializer
)
from .permissions import IsAdminRole, IsAdminOrEditor


# ---------------------------
#  SUBSCRIBE
# ---------------------------
class SubscribeView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=SubscribeSerializer,
        responses={
            201: openapi.Response("Subscription created. Confirm using token sent to email."),
            200: "Already subscribed or subscription pending confirmation."
        }
    )
    def post(self, request):
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()

        subscriber, created = Subscriber.objects.get_or_create(email=email)
        if created:
            return Response(
                {
                    "message": "Subscription created. Confirm using token sent to email.",
                    "token": subscriber.token
                },
                status=status.HTTP_201_CREATED
            )

        if subscriber.confirmed:
            return Response({"message": "Already subscribed."}, status=status.HTTP_200_OK)

        subscriber.save(update_fields=["token"])
        return Response(
            {"message": "Subscription pending confirmation.", "token": subscriber.token},
            status=status.HTTP_200_OK
        )


# ---------------------------
#  CONFIRM SUBSCRIPTION
# ---------------------------
class ConfirmSubscriptionView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("token", openapi.IN_QUERY, description="Confirmation token", type=openapi.TYPE_STRING)
        ],
        responses={200: "Subscription confirmed", 400: "Token required", 404: "Subscriber not found"}
    )
    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({"detail": "Token required."}, status=status.HTTP_400_BAD_REQUEST)

        subscriber = get_object_or_404(Subscriber, token=token)
        subscriber.confirmed = True
        subscriber.save(update_fields=["confirmed"])
        return Response({"message": "Subscription confirmed."}, status=status.HTTP_200_OK)


# ---------------------------
#  UNSUBSCRIBE
# ---------------------------
class UnsubscribeView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UnsubscribeSerializer,
        responses={200: "Unsubscribed successfully", 404: "Subscriber not found"}
    )
    def post(self, request):
        serializer = UnsubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()

        try:
            sub = Subscriber.objects.get(email=email)
            sub.delete()
            return Response({"message": "Unsubscribed successfully."}, status=status.HTTP_200_OK)
        except Subscriber.DoesNotExist:
            return Response({"detail": "Subscriber not found."}, status=status.HTTP_404_NOT_FOUND)


# ---------------------------
#  PREFERENCES (Authenticated only)
# ---------------------------
class PreferenceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: SubscriptionPreferenceSerializer})
    def get(self, request):
        pref, _ = SubscriptionPreference.objects.get_or_create(user=request.user)
        serializer = SubscriptionPreferenceSerializer(pref)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=SubscriptionPreferenceSerializer, responses={201: SubscriptionPreferenceSerializer})
    def post(self, request):
        if hasattr(request.user, "subscription_pref"):
            return Response(
                {"detail": "Preferences already exist. Use PUT to update."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = SubscriptionPreferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=SubscriptionPreferenceSerializer, responses={200: SubscriptionPreferenceSerializer})
    def put(self, request):
        pref, _ = SubscriptionPreference.objects.get_or_create(user=request.user)
        serializer = SubscriptionPreferenceSerializer(pref, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @swagger_auto_schema(responses={204: "Preferences deleted"})
    def delete(self, request):
        pref = get_object_or_404(SubscriptionPreference, user=request.user)
        pref.delete()
        return Response({"message": "Preferences deleted."}, status=status.HTTP_204_NO_CONTENT)


# ---------------------------
#  CAMPAIGNS (Admin only)
# ---------------------------
class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all().order_by("-created_at")
    serializer_class = CampaignSerializer
    permission_classes = [IsAdminRole]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# ---------------------------
#  SUBSCRIPTIONS LIST (Admin/Editor)
# ---------------------------
class SubscriptionListView(generics.ListAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = [IsAdminOrEditor]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscribeView, ConfirmSubscriptionView, UnsubscribeView,
    PreferenceDetailView, CampaignViewSet, SubscriptionListView
)

router = DefaultRouter()
router.register(r"campaigns", CampaignViewSet, basename="campaign")

urlpatterns = [
    path("subscribe/", SubscribeView.as_view(), name="newsletter-subscribe"),
    path("confirm/", ConfirmSubscriptionView.as_view(), name="newsletter-confirm"),
    path("unsubscribe/", UnsubscribeView.as_view(), name="newsletter-unsubscribe"),
    path("preferences/", PreferenceDetailView.as_view(), name="newsletter-preferences"),
    path("subscribers/", SubscriptionListView.as_view(), name="newsletter-subscribers"),
    path("", include(router.urls)),
]

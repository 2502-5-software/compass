from rest_framework import serializers
from .models import Subscriber, SubscriptionPreference, Campaign
from newsapp.models import Category
from django.contrib.auth import get_user_model

User = get_user_model()


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ["email"]


class UnsubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]
        ref_name = "SupscriptionsCategory"


class SubscriptionPreferenceSerializer(serializers.ModelSerializer):
    topics = CategorySerializer(many=True, read_only=True)
    topic_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, write_only=True, source="topics"
    )

    class Meta:
        model = SubscriptionPreference
        fields = ["frequency", "topics", "topic_ids"]


class CampaignSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.id")

    class Meta:
        model = Campaign
        fields = ["id", "title", "content", "scheduled_at", "created_by", "created_at"]
        read_only_fields = ["id", "created_by", "created_at"]

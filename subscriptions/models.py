from django.db import models
from django.conf import settings
from uuid import uuid4
from newsapp.models import Category 


def generate_token():
    return uuid4().hex


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=64, default=generate_token, unique=True)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} ({'confirmed' if self.confirmed else 'unconfirmed'})"


class SubscriptionPreference(models.Model):
    FREQUENCY_CHOICES = (
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription_pref"
    )
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="weekly")
    topics = models.ManyToManyField(Category, related_name="preferences", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user}"


class Campaign(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campaigns"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

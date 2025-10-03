from django.contrib import admin
from .models import Subscriber, SubscriptionPreference, Campaign

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "confirmed", "created_at")
    search_fields = ("email",)

@admin.register(SubscriptionPreference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "frequency", "updated_at")
    search_fields = ("user__email", "user__username")

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("title", "scheduled_at", "created_by", "created_at")
    search_fields = ("title",)
    list_filter = ("scheduled_at", "created_at")    
    readonly_fields = ("created_by", "created_at")
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
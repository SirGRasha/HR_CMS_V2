from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "recipient",
        "notification_type",
        "title",
        "is_read",
        "created_at",
    ]

    list_filter = [
        "notification_type",
        "is_read",
        "created_at",
    ]

    search_fields = [
        "title",
        "message",
        "recipient__username",
        "related_model",
        "related_object_id",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "read_at",
    ]
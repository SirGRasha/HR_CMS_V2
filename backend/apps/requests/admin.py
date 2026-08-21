from django.contrib import admin

from .models import HRRequest


@admin.register(HRRequest)
class HRRequestAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "employee",
        "request_type",
        "title",
        "status",
        "requested_by",
        "reviewed_by",
        "created_at",
    ]

    list_filter = [
        "request_type",
        "status",
        "created_at",
    ]

    search_fields = [
        "title",
        "description",
        "employee__first_name",
        "employee__last_name",
        "requested_by__username",
    ]

    readonly_fields = [
        "requested_by",
        "reviewed_by",
        "reviewed_at",
        "created_at",
        "updated_at",
    ]
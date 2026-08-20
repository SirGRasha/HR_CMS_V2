from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "title",
        "document_type",
        "is_verified",
        "expiry_date",
        "uploaded_by",
        "uploaded_at",
    ]

    list_filter = [
        "document_type",
        "is_verified",
        "expiry_date",
    ]

    search_fields = [
        "title",
        "description",
    ]

    readonly_fields = [
        "uploaded_at",
        "updated_at",
    ]
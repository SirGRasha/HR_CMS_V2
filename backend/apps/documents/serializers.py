import os

from django.utils import timezone
from rest_framework import serializers

from .models import Document


MAX_DOCUMENT_SIZE = 10 * 1024 * 1024

ALLOWED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
}


class DocumentSerializer(serializers.ModelSerializer):

    expiry_status = serializers.SerializerMethodField()

    class Meta:
        model = Document

        fields = [
            "id",
            "document_type",
            "title",
            "description",
            "file",
            "expiry_date",
            "expiry_status",
            "is_verified",
            "uploaded_by",
            "uploaded_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "uploaded_by",
            "uploaded_at",
            "updated_at",
            "expiry_status",
        ]

    def get_expiry_status(self, obj):

        if obj.expiry_date is None:
            return "no_expiry"

        today = timezone.localdate()

        if obj.expiry_date < today:
            return "expired"

        return "valid"

    def validate_file(self, value):

        if value.size > MAX_DOCUMENT_SIZE:
            raise serializers.ValidationError(
                "حجم فایل نباید بیشتر از ۱۰ مگابایت باشد."
            )

        extension = os.path.splitext(
            value.name
        )[1].lower()

        if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise serializers.ValidationError(
                "فرمت فایل مجاز نیست."
            )

        return value

    def validate_expiry_date(self, value):

        if value and value < timezone.localdate():
            raise serializers.ValidationError(
                "تاریخ انقضا نمی‌تواند در گذشته باشد."
            )

        return value
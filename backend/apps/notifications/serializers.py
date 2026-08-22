from django.utils import timezone

from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):

    notification_type_display = serializers.CharField(
        source="get_notification_type_display",
        read_only=True,
    )

    class Meta:
        model = Notification

        fields = [
            "id",
            "recipient",
            "notification_type",
            "notification_type_display",
            "title",
            "message",
            "link",
            "related_model",
            "related_object_id",
            "is_read",
            "read_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "notification_type_display",
            "read_at",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")

        if not (
            request
            and request.user.is_authenticated
            and request.user.is_staff
        ):
            self.fields["recipient"].read_only = True

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Title cannot be empty."
            )

        return value

    def update(self, instance, validated_data):
        if validated_data.get("is_read") is True:
            instance.is_read = True

            if instance.read_at is None:
                instance.read_at = timezone.now()

        elif validated_data.get("is_read") is False:
            instance.is_read = False
            instance.read_at = None

        return super().update(
            instance,
            validated_data,
        )
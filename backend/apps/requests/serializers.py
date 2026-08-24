from django.utils import timezone

from rest_framework import serializers

from .models import HRRequest


class HRRequestSerializer(serializers.ModelSerializer):

    request_type_display = serializers.CharField(
        source="get_request_type_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    requested_by_username = serializers.CharField(
        source="requested_by.username",
        read_only=True,
    )

    reviewed_by_username = serializers.CharField(
        source="reviewed_by.username",
        read_only=True,
    )

    class Meta:
        model = HRRequest

        fields = [
            "id",
            "employee",
            "requested_by",
            "requested_by_username",
            "request_type",
            "request_type_display",
            "title",
            "description",
            "status",
            "status_display",
            "response",
            "reviewed_by",
            "reviewed_by_username",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "requested_by",
            "requested_by_username",
            "request_type_display",
            "status_display",
            "reviewed_by",
            "reviewed_by_username",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Title cannot be empty."
            )

        return value

    def validate(self, attrs):
        request = self.context.get("request")
        instance = self.instance

        if not request:
            raise serializers.ValidationError(
                "Request context is required."
            )

        # ---------------------------------------------------------
        # Finalized requests are immutable.
        # ---------------------------------------------------------
        if (
            instance
            and instance.status
            in [
                HRRequest.Status.APPROVED,
                HRRequest.Status.REJECTED,
                HRRequest.Status.CANCELLED,
            ]
        ):
            raise serializers.ValidationError(
                "Finalized requests cannot be modified."
            )

        # ---------------------------------------------------------
        # Normal users cannot modify protected fields.
        # ---------------------------------------------------------
        if (
            instance
            and not request.user.is_staff
        ):
            protected_fields = {
                "employee": (
                    "Employee cannot be changed "
                    "after request creation."
                ),
                "request_type": (
                    "Request type cannot be changed "
                    "after request creation."
                ),
                "response": (
                    "Response can only be changed "
                    "by staff users."
                ),
                "status": (
                    "Only staff users can change "
                    "request status."
                ),
            }

            errors = {}

            for field, message in protected_fields.items():
                if field in attrs:
                    errors[field] = message

            if errors:
                raise serializers.ValidationError(errors)

        # ---------------------------------------------------------
        # Status changes are only allowed for staff.
        # ---------------------------------------------------------
        if (
            instance
            and "status" in attrs
            and not request.user.is_staff
        ):
            raise serializers.ValidationError(
                {
                    "status": (
                        "Only staff users can change "
                        "request status."
                    )
                }
            )

        # ---------------------------------------------------------
        # Explicit state transition validation.
        # ---------------------------------------------------------
        if (
            instance
            and "status" in attrs
        ):
            current_status = instance.status
            new_status = attrs["status"]

            if (
                current_status
                != HRRequest.Status.PENDING
            ):
                raise serializers.ValidationError(
                    {
                        "status": (
                            "Only pending requests "
                            "can change status."
                        )
                    }
                )

            allowed_statuses = {
                HRRequest.Status.PENDING,
                HRRequest.Status.APPROVED,
                HRRequest.Status.REJECTED,
                HRRequest.Status.CANCELLED,
            }

            if new_status not in allowed_statuses:
                raise serializers.ValidationError(
                    {
                        "status": "Invalid request status."
                    }
                )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]

        return HRRequest.objects.create(
            requested_by=request.user,
            **validated_data,
        )

    def update(self, instance, validated_data):
        request = self.context.get("request")

        if request and request.user.is_staff:
            new_status = validated_data.get(
                "status",
                instance.status,
            )

            if (
                new_status != HRRequest.Status.PENDING
                and new_status != instance.status
            ):
                instance.reviewed_by = request.user
                instance.reviewed_at = timezone.now()

        return super().update(
            instance,
            validated_data,
        )
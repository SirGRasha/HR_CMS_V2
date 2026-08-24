from rest_framework import serializers

from .models import Correspondence


class CorrespondenceSerializer(serializers.ModelSerializer):

    correspondence_type_display = serializers.CharField(
        source="get_correspondence_type_display",
        read_only=True,
    )

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    employee_name = serializers.SerializerMethodField()

    organization_unit_name = serializers.SerializerMethodField()

    class Meta:
        model = Correspondence

        fields = [
            "id",
            "correspondence_type",
            "correspondence_type_display",
            "letter_number",
            "letter_date",
            "subject",
            "body",
            "sender",
            "recipient",
            "employee",
            "employee_name",
            "organization_unit",
            "organization_unit_name",
            "status",
            "status_display",
            "created_by",
            "created_by_username",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "correspondence_type_display",
            "status_display",
            "created_by",
            "created_by_username",
            "employee_name",
            "organization_unit_name",
            "created_at",
            "updated_at",
        ]

    def get_employee_name(self, obj):
        if not obj.employee:
            return None

        return str(obj.employee)

    def get_organization_unit_name(self, obj):
        if not obj.organization_unit:
            return None

        return str(obj.organization_unit)

    def validate_letter_number(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Letter number cannot be empty."
            )

        return value

    def validate_subject(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Subject cannot be empty."
            )

        return value

    def validate_sender(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Sender cannot be empty."
            )

        return value

    def validate_recipient(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Recipient cannot be empty."
            )

        return value

    def validate_status(self, value):
        """
        Validate correspondence status transitions.

        Allowed workflow:

            DRAFT -> REGISTERED
            REGISTERED -> SENT
            REGISTERED -> RECEIVED
            SENT -> RECEIVED
            SENT -> ARCHIVED
            RECEIVED -> ARCHIVED

        Backward transitions and skipping states are not allowed.
        """

        if not self.instance:
            return value

        current_status = self.instance.status

        if current_status == value:
            return value

        allowed_transitions = {
            Correspondence.Status.DRAFT: {
                Correspondence.Status.REGISTERED,
            },
            Correspondence.Status.REGISTERED: {
                Correspondence.Status.SENT,
                Correspondence.Status.RECEIVED,
            },
            Correspondence.Status.SENT: {
                Correspondence.Status.RECEIVED,
                Correspondence.Status.ARCHIVED,
            },
            Correspondence.Status.RECEIVED: {
                Correspondence.Status.ARCHIVED,
            },
            Correspondence.Status.ARCHIVED: set(),
        }

        allowed_statuses = allowed_transitions.get(
            current_status,
            set(),
        )

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                "Invalid correspondence status transition."
            )

        return value
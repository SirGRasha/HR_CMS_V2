from rest_framework import serializers

from apps.organization.models import OrganizationUnit, Position


class OrganizationUnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationUnit
        fields = [
            "id",
            "code",
            "name",
            "unit_type",
            "parent",
            "is_active",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class PositionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Position
        fields = [
            "id",
            "code",
            "title",
            "organization_unit",
            "is_active",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

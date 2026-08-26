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

    def validate(self, attrs):
        parent = attrs.get("parent")

        # No parent means this is a root unit.
        if parent is None:
            return attrs

        instance = self.instance

        # On update, a unit cannot be its own parent.
        if instance and parent.pk == instance.pk:
            raise serializers.ValidationError(
                {
                    "parent": (
                        "An organization unit cannot "
                        "be its own parent."
                    )
                }
            )

        # On update, prevent creating a cycle in the tree.
        if instance:
            current = parent

            while current is not None:
                if current.pk == instance.pk:
                    raise serializers.ValidationError(
                        {
                            "parent": (
                                "This parent would create "
                                "a cycle in the organization tree."
                            )
                        }
                    )

                current = current.parent

        return attrs


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
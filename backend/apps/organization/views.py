from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.organization.models import OrganizationUnit, Position
from apps.organization.serializers import (
    OrganizationUnitSerializer,
    PositionSerializer,
)


class OrganizationUnitViewSet(viewsets.ModelViewSet):
    """
    API مدیریت واحدهای سازمانی.
    """

    queryset = (
        OrganizationUnit.objects
        .select_related("parent")
        .all()
        .order_by("name")
    )

    serializer_class = OrganizationUnitSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        is_active = self.request.query_params.get("is_active")
        unit_type = self.request.query_params.get("unit_type")
        parent = self.request.query_params.get("parent")

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(is_active=False)

        if unit_type:
            queryset = queryset.filter(
                unit_type=unit_type
            )

        if parent:
            if parent.lower() == "null":
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(
                    parent_id=parent
                )

        return queryset
    pagination_class = None


class PositionViewSet(viewsets.ModelViewSet):
    """
    API مدیریت سمت‌های سازمانی.
    """

    queryset = (
        Position.objects
        .select_related("organization_unit")
        .all()
        .order_by("title")
    )

    serializer_class = PositionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        is_active = self.request.query_params.get("is_active")
        organization_unit = self.request.query_params.get(
            "organization_unit"
        )

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(is_active=False)

        if organization_unit:
            queryset = queryset.filter(
                organization_unit_id=organization_unit
            )

        return queryset
    pagination_class = None

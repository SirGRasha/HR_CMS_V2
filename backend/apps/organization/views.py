from rest_framework import viewsets

from apps.organization.models import (
    OrganizationUnit,
    Position,
)
from apps.organization.permissions import (
    IsAuthenticatedOrStaffWrite,
)
from apps.organization.serializers import (
    OrganizationUnitSerializer,
    PositionSerializer,
)
from apps.audit.services import AuditService
from apps.audit.utils import build_changes


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
    permission_classes = [
        IsAuthenticatedOrStaffWrite
    ]

    AUDIT_UPDATE_FIELDS = [
        "code",
        "name",
        "unit_type",
        "parent_id",
        "is_active",
        "description",
    ]

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

    def perform_create(self, serializer):
        instance = serializer.save()

        AuditService.create(
            actor=self.request.user,
            instance=instance,
            request=self.request,
        )

    def perform_update(self, serializer):
        old_instance = OrganizationUnit.objects.get(
            pk=serializer.instance.pk
        )

        instance = serializer.save()

        changes = build_changes(
            old_instance,
            instance,
            self.AUDIT_UPDATE_FIELDS,
        )

        if changes:
            AuditService.update(
                actor=self.request.user,
                instance=instance,
                request=self.request,
                changes=changes,
            )

    def perform_destroy(self, instance):
        AuditService.delete(
            actor=self.request.user,
            instance=instance,
            request=self.request,
        )

        instance.delete()


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
    permission_classes = [
        IsAuthenticatedOrStaffWrite
    ]

    AUDIT_UPDATE_FIELDS = [
        "code",
        "title",
        "organization_unit_id",
        "is_active",
        "description",
    ]

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

    def perform_create(self, serializer):
        instance = serializer.save()

        AuditService.create(
            actor=self.request.user,
            instance=instance,
            request=self.request,
        )

    def perform_update(self, serializer):
        old_instance = Position.objects.get(
            pk=serializer.instance.pk
        )

        instance = serializer.save()

        changes = build_changes(
            old_instance,
            instance,
            self.AUDIT_UPDATE_FIELDS,
        )

        if changes:
            AuditService.update(
                actor=self.request.user,
                instance=instance,
                request=self.request,
                changes=changes,
            )

    def perform_destroy(self, instance):
        AuditService.delete(
            actor=self.request.user,
            instance=instance,
            request=self.request,
        )

        instance.delete()

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.audit.models import AuditLog
from apps.audit.permissions import IsAuditViewer
from apps.audit.serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        AuditLog.objects
        .select_related("actor")
        .all()
    )

    serializer_class = AuditLogSerializer
    permission_classes = [IsAuditViewer]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "actor",
        "action",
        "app_label",
        "model_name",
        "object_id",
    ]

    search_fields = [
        "object_repr",
        "actor__username",
        "actor__first_name",
        "actor__last_name",
    ]

    ordering_fields = [
        "created_at",
        "action",
        "app_label",
        "model_name",
    ]

    ordering = [
        "-created_at",
    ]
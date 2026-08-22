from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.audit.services import AuditService

from .models import Correspondence
from .permissions import CorrespondencePermission
from .serializers import CorrespondenceSerializer


class CorrespondenceViewSet(viewsets.ModelViewSet):

    queryset = (
        Correspondence.objects
        .select_related(
            "employee",
            "organization_unit",
            "created_by",
        )
        .all()
        .order_by(
            "-letter_date",
            "-id",
        )
    )

    serializer_class = CorrespondenceSerializer

    permission_classes = [
        IsAuthenticated,
        CorrespondencePermission,
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        correspondence_type = (
            self.request.query_params.get(
                "correspondence_type"
            )
        )

        status = self.request.query_params.get(
            "status"
        )

        employee = self.request.query_params.get(
            "employee"
        )

        organization_unit = (
            self.request.query_params.get(
                "organization_unit"
            )
        )

        letter_number = (
            self.request.query_params.get(
                "letter_number"
            )
        )

        if correspondence_type:
            queryset = queryset.filter(
                correspondence_type=correspondence_type
            )

        if status:
            queryset = queryset.filter(
                status=status
            )

        if employee:
            queryset = queryset.filter(
                employee_id=employee
            )

        if organization_unit:
            queryset = queryset.filter(
                organization_unit_id=organization_unit
            )

        if letter_number:
            queryset = queryset.filter(
                letter_number__icontains=letter_number
            )

        return queryset

    def perform_create(self, serializer):
        instance = serializer.save(
            created_by=self.request.user
        )

        AuditService.create(
            actor=self.request.user,
            instance=instance,
            request=self.request,
        )

    def perform_update(self, serializer):
        old_instance = Correspondence.objects.get(
            pk=serializer.instance.pk
        )

        instance = serializer.save()

        changes = {}

        fields = [
            "correspondence_type",
            "letter_number",
            "letter_date",
            "subject",
            "body",
            "sender",
            "recipient",
            "employee_id",
            "organization_unit_id",
            "status",
        ]

        for field in fields:
            old_value = getattr(
                old_instance,
                field,
            )

            new_value = getattr(
                instance,
                field,
            )

            if old_value != new_value:
                changes[field] = {
                    "old": old_value,
                    "new": new_value,
                }

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
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.audit.services import AuditService
from apps.notifications.models import Notification
from apps.notifications.services.notification_service import (
    NotificationService,
)

from .models import HRRequest
from .permissions import HRRequestPermission
from .serializers import HRRequestSerializer


class HRRequestViewSet(viewsets.ModelViewSet):

    queryset = (
        HRRequest.objects
        .select_related(
            "employee",
            "requested_by",
            "reviewed_by",
        )
        .all()
        .order_by(
            "-created_at",
            "-id",
        )
    )

    serializer_class = HRRequestSerializer

    permission_classes = [
        IsAuthenticated,
        HRRequestPermission,
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        if not user.is_staff:
            queryset = queryset.filter(
                requested_by=user
            )

        employee = self.request.query_params.get(
            "employee"
        )

        request_type = self.request.query_params.get(
            "request_type"
        )

        status = self.request.query_params.get(
            "status"
        )

        if employee:
            queryset = queryset.filter(
                employee_id=employee
            )

        if request_type:
            queryset = queryset.filter(
                request_type=request_type
            )

        if status:
            queryset = queryset.filter(
                status=status
            )

        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()

        AuditService.create(
            actor=self.request.user,
            instance=instance,
            request=self.request,
        )

    def perform_update(self, serializer):
        old_instance = HRRequest.objects.get(
            pk=serializer.instance.pk
        )

        instance = serializer.save()

        changes = {}

        fields = [
            "employee_id",
            "request_type",
            "title",
            "description",
            "status",
            "response",
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

        if (
            old_instance.status
            != instance.status
            and instance.status
            in [
                HRRequest.Status.APPROVED,
                HRRequest.Status.REJECTED,
            ]
        ):
            if instance.status == HRRequest.Status.APPROVED:
                notification_type = (
                    Notification.NotificationType.SUCCESS
                )

                title = "درخواست شما تأیید شد"

                message = (
                    f"درخواست «{instance.title}» "
                    "با موفقیت تأیید شد."
                )

            else:
                notification_type = (
                    Notification.NotificationType.ERROR
                )

                title = "درخواست شما رد شد"

                message = (
                    f"درخواست «{instance.title}» "
                    "رد شد."
                )

            NotificationService.create(
                recipient=instance.requested_by,
                notification_type=notification_type,
                title=title,
                message=message,
                link=(
                    f"/api/requests/requests/"
                    f"{instance.id}/"
                ),
                related_model="HRRequest",
                related_object_id=str(instance.id),
            )

    def perform_destroy(self, instance):
        AuditService.delete(
            actor=self.request.user,
            instance=instance,
            request=self.request,
        )

        instance.delete()
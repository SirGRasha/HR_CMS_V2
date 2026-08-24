from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification
from .permissions import NotificationPermission
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):

    serializer_class = NotificationSerializer

    permission_classes = [
        IsAuthenticated,
        NotificationPermission,
    ]

    queryset = (
        Notification.objects
        .select_related("recipient")
        .all()
        .order_by(
            "-created_at",
            "-id",
        )
    )

    def get_queryset(self):
        queryset = super().get_queryset()

        if not self.request.user.is_staff:
            queryset = queryset.filter(
                recipient=self.request.user
            )

        is_read = self.request.query_params.get(
            "is_read"
        )

        notification_type = self.request.query_params.get(
            "notification_type"
        )

        if is_read is not None:
            if is_read.lower() in ["true", "1"]:
                queryset = queryset.filter(
                    is_read=True
                )
            elif is_read.lower() in ["false", "0"]:
                queryset = queryset.filter(
                    is_read=False
                )

        if notification_type:
            queryset = queryset.filter(
                notification_type=notification_type
            )

        return queryset

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save()
        else:
            serializer.save(
                recipient=self.request.user
            )

    @action(
        detail=True,
        methods=["post"],
        url_path="read",
    )
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()

        if (
            not notification.is_read
            or notification.read_at is None
        ):
            notification.is_read = True

            if notification.read_at is None:
                notification.read_at = timezone.now()

            notification.save(
                update_fields=[
                    "is_read",
                    "read_at",
                    "updated_at",
                ]
            )

        serializer = self.get_serializer(
            notification
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="mark-all-read",
    )
    def mark_all_as_read(self, request):
        updated_count = (
            self.get_queryset()
            .filter(is_read=False)
            .update(
                is_read=True,
                read_at=timezone.now(),
                updated_at=timezone.now(),
            )
        )

        return Response(
            {
                "detail": (
                    "All notifications marked "
                    "as read."
                ),
                "updated_count": updated_count,
            },
            status=status.HTTP_200_OK,
        )
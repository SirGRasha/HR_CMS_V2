from django.utils import timezone

from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import Document
from .permissions import DocumentPermission
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):

    queryset = (
        Document.objects
        .select_related("uploaded_by")
        .all()
        .order_by("-uploaded_at")
    )

    serializer_class = DocumentSerializer

    permission_classes = [
        IsAuthenticated,
        DocumentPermission,
    ]

    def get_queryset(self):

        queryset = super().get_queryset()

        if not self.request.user.is_staff:
            queryset = queryset.filter(
                uploaded_by=self.request.user
            )

        document_type = self.request.query_params.get(
            "document_type"
        )

        is_verified = self.request.query_params.get(
            "is_verified"
        )

        expiry_status = self.request.query_params.get(
            "expiry_status"
        )

        if document_type:
            queryset = queryset.filter(
                document_type=document_type
            )

        if is_verified is not None:

            if is_verified.lower() == "true":
                queryset = queryset.filter(
                    is_verified=True
                )

            elif is_verified.lower() == "false":
                queryset = queryset.filter(
                    is_verified=False
                )

            else:
                raise ValidationError(
                    {
                        "is_verified": (
                            "Invalid value. "
                            "Allowed values are: true, false."
                        )
                    }
                )

        if expiry_status:

            allowed_expiry_statuses = {
                "expired",
                "valid",
                "no_expiry",
            }

            if expiry_status not in allowed_expiry_statuses:
                raise ValidationError(
                    {
                        "expiry_status": (
                            "Invalid value. "
                            "Allowed values are: "
                            "expired, valid, no_expiry."
                        )
                    }
                )

        today = timezone.localdate()

        if expiry_status == "expired":
            queryset = queryset.filter(
                expiry_date__lt=today
            )

        elif expiry_status == "valid":
            queryset = queryset.filter(
                expiry_date__gte=today
            )

        elif expiry_status == "no_expiry":
            queryset = queryset.filter(
                expiry_date__isnull=True
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(
            uploaded_by=self.request.user
        )

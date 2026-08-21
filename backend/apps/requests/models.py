from django.conf import settings
from django.db import models


class HRRequest(models.Model):

    class RequestType(models.TextChoices):
        LEAVE = "LEAVE", "Leave"
        LOAN = "LOAN", "Loan"
        ADVANCE = "ADVANCE", "Advance"
        CERTIFICATE = "CERTIFICATE", "Certificate"
        PERSONNEL = "PERSONNEL", "Personnel"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    employee = models.ForeignKey(
        "personnel.Employee",
        on_delete=models.PROTECT,
        related_name="hr_requests",
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="hr_requests",
    )

    request_type = models.CharField(
        max_length=30,
        choices=RequestType.choices,
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    response = models.TextField(
        blank=True,
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_hr_requests",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at", "-id"]

        indexes = [
            models.Index(
                fields=["employee", "-created_at"],
            ),
            models.Index(
                fields=["requested_by", "-created_at"],
            ),
            models.Index(
                fields=["status", "-created_at"],
            ),
            models.Index(
                fields=["request_type", "-created_at"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.get_request_type_display()} - "
            f"{self.title} - "
            f"{self.get_status_display()}"
        )

from django.conf import settings
from django.db import models


class Correspondence(models.Model):

    class CorrespondenceType(models.TextChoices):
        INCOMING = "INCOMING", "Incoming"
        OUTGOING = "OUTGOING", "Outgoing"
        INTERNAL = "INTERNAL", "Internal"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        REGISTERED = "REGISTERED", "Registered"
        SENT = "SENT", "Sent"
        RECEIVED = "RECEIVED", "Received"
        ARCHIVED = "ARCHIVED", "Archived"

    correspondence_type = models.CharField(
        max_length=20,
        choices=CorrespondenceType.choices,
    )

    letter_number = models.CharField(
        max_length=100,
    )

    letter_date = models.DateField()

    subject = models.CharField(
        max_length=255,
    )

    body = models.TextField(
        blank=True,
    )

    sender = models.CharField(
        max_length=255,
    )

    recipient = models.CharField(
        max_length=255,
    )

    employee = models.ForeignKey(
        "personnel.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="correspondences",
    )

    organization_unit = models.ForeignKey(
        "organization.OrganizationUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="correspondences",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_correspondences",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-letter_date",
            "-id",
        ]

        indexes = [
            models.Index(
                fields=["letter_number"],
            ),
            models.Index(
                fields=["correspondence_type", "status"],
            ),
            models.Index(
                fields=["employee", "-letter_date"],
            ),
            models.Index(
                fields=["organization_unit", "-letter_date"],
            ),
            models.Index(
                fields=["created_by", "-created_at"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.letter_number} - "
            f"{self.subject}"
        )
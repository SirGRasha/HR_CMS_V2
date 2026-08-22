from django.conf import settings
from django.db import models


class Notification(models.Model):

    class NotificationType(models.TextChoices):
        INFO = "INFO", "Information"
        SUCCESS = "SUCCESS", "Success"
        WARNING = "WARNING", "Warning"
        ERROR = "ERROR", "Error"
        REQUEST = "REQUEST", "Request"
        CORRESPONDENCE = "CORRESPONDENCE", "Correspondence"
        PAYROLL = "PAYROLL", "Payroll"
        DOCUMENT = "DOCUMENT", "Document"
        SYSTEM = "SYSTEM", "System"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
    )

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    link = models.CharField(
        max_length=500,
        blank=True,
    )

    related_model = models.CharField(
        max_length=100,
        blank=True,
    )

    related_object_id = models.CharField(
        max_length=100,
        blank=True,
    )

    is_read = models.BooleanField(
        default=False,
    )

    read_at = models.DateTimeField(
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
                fields=["recipient", "-created_at"],
            ),
            models.Index(
                fields=["recipient", "is_read", "-created_at"],
            ),
            models.Index(
                fields=["notification_type", "-created_at"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.recipient.username} - "
            f"{self.title}"
        )
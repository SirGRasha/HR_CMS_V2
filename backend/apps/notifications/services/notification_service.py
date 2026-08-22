from apps.notifications.models import Notification


class NotificationService:
    """
    Central service for creating notifications.
    """

    @staticmethod
    def create(
        *,
        recipient,
        title,
        message,
        notification_type=Notification.NotificationType.INFO,
        link="",
        related_model="",
        related_object_id="",
    ):
        return Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            related_model=related_model,
            related_object_id=related_object_id,
        )
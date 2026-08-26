from datetime import date, datetime
from decimal import Decimal

from apps.audit.models import AuditLog


class AuditService:

    @staticmethod
    def make_json_safe(value):
        """
        تبدیل مقادیر Python به مقادیری که JSONField بتواند ذخیره کند.
        """

        if isinstance(value, Decimal):
            return str(value)

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, dict):
            return {
                str(key): AuditService.make_json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple)):
            return [
                AuditService.make_json_safe(item)
                for item in value
            ]

        return value

    @staticmethod
    def get_client_ip(request):
        if not request:
            return None

        forwarded_for = request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )

        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def get_user_agent(request):
        if not request:
            return ""

        return request.META.get(
            "HTTP_USER_AGENT",
            "",
        )

    @classmethod
    def log(
        cls,
        *,
        actor=None,
        action,
        instance,
        request=None,
        changes=None,
    ):
        safe_changes = cls.make_json_safe(
            changes or {}
        )

        return AuditLog.objects.create(
            actor=actor,
            action=action,
            app_label=instance._meta.app_label,
            model_name=instance._meta.model_name,
            object_id=(
                str(instance.pk)
                if instance.pk
                else None
            ),
            object_repr=str(instance),
            changes=safe_changes,
            ip_address=cls.get_client_ip(request),
            user_agent=cls.get_user_agent(request),
        )

    @classmethod
    def create(
        cls,
        *,
        actor=None,
        instance,
        request=None,
        changes=None,
    ):
        return cls.log(
            actor=actor,
            action=AuditLog.Action.CREATE,
            instance=instance,
            request=request,
            changes=changes,
        )

    @classmethod
    def update(
        cls,
        *,
        actor=None,
        instance,
        request=None,
        changes=None,
    ):
        return cls.log(
            actor=actor,
            action=AuditLog.Action.UPDATE,
            instance=instance,
            request=request,
            changes=changes,
        )

    @classmethod
    def delete(
        cls,
        *,
        actor=None,
        instance,
        request=None,
        changes=None,
    ):
        return cls.log(
            actor=actor,
            action=AuditLog.Action.DELETE,
            instance=instance,
            request=request,
            changes=changes,
        )

    @classmethod
    def login(
        cls,
        *,
        actor=None,
        instance,
        request=None,
        changes=None,
    ):
        return cls.log(
            actor=actor,
            action=AuditLog.Action.LOGIN,
            instance=instance,
            request=request,
            changes=changes,
        )

    @classmethod
    def logout(
        cls,
        *,
        actor=None,
        instance,
        request=None,
        changes=None,
    ):
        return cls.log(
            actor=actor,
            action=AuditLog.Action.LOGOUT,
            instance=instance,
            request=request,
            changes=changes,
        )

    @classmethod
    def password_change(
        cls,
        *,
        actor=None,
        instance,
        request=None,
        changes=None,
    ):
        return cls.log(
            actor=actor,
            action=AuditLog.Action.PASSWORD_CHANGE,
            instance=instance,
            request=request,
            changes=changes,
        )
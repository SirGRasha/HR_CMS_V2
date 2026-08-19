from rest_framework.permissions import BasePermission


class IsAuditViewer(BasePermission):
    """
    Only authenticated staff users can view audit logs.
    Superusers are also allowed.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
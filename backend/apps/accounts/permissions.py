from rest_framework.permissions import BasePermission


class IsStaffOrReadOnly(BasePermission):
    """
    Staff users can manage users.
    Other authenticated users have no access.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )


class IsSuperuser(BasePermission):
    """
    Only superusers can perform privileged operations.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )


class CanChangeUserPassword(BasePermission):
    """
    A user can change their own password.
    Staff users can change other users' passwords.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj
            or request.user.is_staff
        )
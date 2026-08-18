from rest_framework.permissions import BasePermission


class IsStaffOrReadOnly(BasePermission):
    """
    Staff users can access user management.
    Normal authenticated users have no access.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        """
        Staff users cannot modify staff or superuser accounts.
        Superusers can modify any user account.
        """

        if request.user.is_superuser:
            return True

        if not request.user.is_staff:
            return False

        if obj.is_superuser:
            return False

        if obj.is_staff and obj != request.user:
            return False

        return True


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

    def has_object_permission(self, request, view, obj):
        if not (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        ):
            return False

        # A superuser cannot delete their own account.
        if (
            view.action == "destroy"
            and request.user == obj
        ):
            return False

        return True


class CanChangeUserPassword(BasePermission):
    """
    A user can change their own password.
    Staff users can change normal users' passwords.
    Superusers can change any user's password.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.user == obj:
            return True

        if request.user.is_superuser:
            return True

        if request.user.is_staff and not obj.is_staff and not obj.is_superuser:
            return True

        return False
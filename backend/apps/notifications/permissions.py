from rest_framework.permissions import BasePermission


class NotificationPermission(BasePermission):
    """
    Staff users:
        Full access.

    Normal authenticated users:
        Can view their own notifications.
        Can mark their own notifications as read/unread.
        Can delete their own notifications.
        Cannot create notifications.
        Cannot access other users' notifications.
    """

    def has_permission(self, request, view):
        if not (
            request.user
            and request.user.is_authenticated
        ):
            return False

        # Custom notification actions use POST but are
        # intentionally available to normal users.
        if request.method == "POST":
            if view.action in [
                "mark_as_read",
                "mark_all_as_read",
            ]:
                return True

            # Creating notifications is staff-only.
            return request.user.is_staff

        return True

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if request.user.is_staff:
            return True

        return obj.recipient == request.user
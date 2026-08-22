from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedOrStaffWrite(BasePermission):
    """
    Authenticated users can read organization data.

    Staff and superusers can create, update and delete
    organization units and positions.
    """

    def has_permission(self, request, view):
        if not (
            request.user
            and request.user.is_authenticated
        ):
            return False

        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user.is_staff
            or request.user.is_superuser
        )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.is_superuser
            )
        )
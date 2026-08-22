from rest_framework.permissions import BasePermission


class CorrespondencePermission(BasePermission):
    """
    Staff:
        Full access.

    Normal authenticated users:
        Can create correspondence.
        Can view correspondence.
        Cannot modify or delete correspondence.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        if request.user.is_staff:
            return True

        if request.method in [
            "GET",
            "HEAD",
            "OPTIONS",
        ]:
            return True

        return False
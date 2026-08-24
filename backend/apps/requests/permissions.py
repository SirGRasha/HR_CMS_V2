from rest_framework.permissions import BasePermission


class HRRequestPermission(BasePermission):
    """
    Staff users:
        Can access all requests.
        Can modify pending requests.
        Cannot modify finalized requests because the serializer
        enforces finalized-request protection.
        Cannot delete finalized requests.

    Normal authenticated users:
        Can create requests.
        Can view their own requests.
        Can modify their own pending requests.
        Cannot modify another user's requests.
        Cannot change request status.
        Can delete their own pending requests.
        Cannot delete finalized requests.
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
        # Staff users can access all request objects,
        # but finalized requests are protected below.
        if request.user.is_staff:
            if request.method == "DELETE":
                return (
                    obj.status
                    == obj.Status.PENDING
                )

            return True

        # Normal users can only access their own requests.
        if obj.requested_by != request.user:
            return False

        # Read-only access is allowed for the owner.
        if request.method in [
            "GET",
            "HEAD",
            "OPTIONS",
        ]:
            return True

        # PUT/PATCH reaches the serializer.
        # The serializer blocks finalized requests.
        if request.method in [
            "PUT",
            "PATCH",
        ]:
            return True

        # DELETE is allowed only for pending requests.
        if request.method == "DELETE":
            return (
                obj.status
                == obj.Status.PENDING
            )

        return False
from rest_framework.permissions import BasePermission


class HRRequestPermission(BasePermission):
    """
    Staff:
        Full access, subject to business rules enforced by the serializer.

    Normal authenticated users:
        Can create requests.
        Can view their own requests.
        Can modify their own pending requests.
        Cannot approve/reject/cancel requests.
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
        # Staff users can access all request objects.
        # Business rules such as finalized-request protection
        # are enforced at the serializer/service layer.
        if request.user.is_staff:
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

        # For PUT/PATCH, allow the owner to reach the serializer.
        # The serializer is responsible for returning 400 when
        # the request has already been finalized.
        if request.method in [
            "PUT",
            "PATCH",
        ]:
            return True

        # DELETE is different because serializers are not involved.
        # Therefore finalized requests must be blocked here.
        if request.method == "DELETE":
            return (
                obj.status
                == obj.Status.PENDING
            )

        return False
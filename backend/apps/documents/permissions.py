from rest_framework.permissions import BasePermission


class DocumentPermission(BasePermission):
    """
    Staff users:
        Full access to all documents.

    Normal authenticated users:
        Can create documents.
        Can view their own documents.
        Can modify their own documents.
        Can delete their own documents.
        Cannot access other users' documents.
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

        return obj.uploaded_by == request.user
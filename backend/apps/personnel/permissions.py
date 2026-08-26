from rest_framework.permissions import BasePermission, SAFE_METHODS


class PersonnelPermission(BasePermission):
    """
    Personnel access policy.

    Staff / Superusers:
        Full CRUD access.

    Normal authenticated users:
        Employee:
            Read-only access to their own employee record.

        Related personnel records:
            Full CRUD access only for records belonging
            to their own employee.

    Anonymous users:
        No access.
    """

    def has_permission(self, request, view):
        # Anonymous users have no access.
        if not (
            request.user
            and request.user.is_authenticated
        ):
            return False

        # Staff and superusers have full access.
        if (
            request.user.is_staff
            or request.user.is_superuser
        ):
            return True

        # EmployeeViewSet is read-only for normal users.
        if view.__class__.__name__ == "EmployeeViewSet":
            return request.method in SAFE_METHODS

        # Document records are read-only for normal users.
        if view.__class__.__name__ == "EmployeeDocumentViewSet":
            return request.method in SAFE_METHODS

        # Related personnel records can be managed
        # by their owning normal user.
        return True

    def has_object_permission(
        self,
        request,
        view,
        obj,
    ):
        # Staff and superusers can access everything.
        if (
            request.user.is_staff
            or request.user.is_superuser
        ):
            return True

        # Employee object.
        if hasattr(obj, "user"):
            # Normal users can only access their own employee.
            # Employee itself remains read-only.
            if obj.user != request.user:
                return False

            return request.method in SAFE_METHODS

        # Related personnel objects.
        employee = getattr(obj, "employee", None)

        if employee is not None:
            # Must belong to the authenticated user's employee.
            if employee.user != request.user:
                return False

            # Owner can CRUD related records.
            return True

        return False
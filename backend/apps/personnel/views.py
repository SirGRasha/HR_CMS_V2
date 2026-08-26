from rest_framework import viewsets
from django.utils import timezone

from .models import Employee
from .models import EmployeeChild
from .models import EmployeeDocument
from .models import EmployeePhone
from .models import EmployeePromissoryNote
from .models import EmployeeBankAccount
from .permissions import PersonnelPermission

from .serializers import EmployeeSerializer
from .serializers import EmployeeChildSerializer
from .serializers import EmployeeDocumentSerializer
from .serializers import EmployeePhoneSerializer
from .serializers import EmployeePromissoryNoteSerializer
from .serializers import EmployeeBankAccountSerializer


class EmployeeViewSet(viewsets.ModelViewSet):

    permission_classes = [
        PersonnelPermission,
    ]

    queryset = (
        Employee.objects
        .select_related(
            "position",
            "position__organization_unit",
        )
        .all()
        .order_by(
            "last_name",
            "first_name",
        )
    )

    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if not (
            self.request.user.is_staff
            or self.request.user.is_superuser
        ):
            queryset = queryset.filter(
                user=self.request.user
            )

        position = self.request.query_params.get("position")
        organization_unit = self.request.query_params.get(
            "organization_unit"
        )
        is_active = self.request.query_params.get("is_active")
        employee_group = self.request.query_params.get(
            "employee_group"
        )

        if position:
            queryset = queryset.filter(
                position_id=position
            )

        if organization_unit:
            queryset = queryset.filter(
                position__organization_unit_id=organization_unit
            )

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(is_active=True)

            elif is_active.lower() == "false":
                queryset = queryset.filter(is_active=False)

        if employee_group:
            queryset = queryset.filter(
                employee_group=employee_group
            )

        return queryset


class EmployeeChildViewSet(viewsets.ModelViewSet):

    permission_classes = [
        PersonnelPermission,
    ]

    queryset = EmployeeChild.objects.all().order_by(
        "employee",
        "birth_date",
    )

    serializer_class = EmployeeChildSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if not (
            self.request.user.is_staff
            or self.request.user.is_superuser
        ):
            queryset = queryset.filter(
                employee__user=self.request.user
            )

        return queryset

class EmployeePhoneViewSet(viewsets.ModelViewSet):

    permission_classes = [
        PersonnelPermission,
    ]

    queryset = EmployeePhone.objects.all().order_by(
        "employee",
        "-is_primary",
        "phone_number",
    )

    serializer_class = EmployeePhoneSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if not (
            self.request.user.is_staff
            or self.request.user.is_superuser
        ):
            queryset = queryset.filter(
                employee__user=self.request.user
            )

        employee_id = self.request.query_params.get("employee")

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id
            )

        return queryset

class EmployeeBankAccountViewSet(viewsets.ModelViewSet):

    permission_classes = [
        PersonnelPermission,
    ]

    queryset = EmployeeBankAccount.objects.all().order_by(
        "employee",
        "-is_primary",
        "bank_name",
    )

    serializer_class = EmployeeBankAccountSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if not (
            self.request.user.is_staff
            or self.request.user.is_superuser
        ):
            queryset = queryset.filter(
                employee__user=self.request.user
            )

        employee_id = self.request.query_params.get("employee")

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id
            )

        return queryset

    pagination_class = None

class EmployeePromissoryNoteViewSet(viewsets.ModelViewSet):

    permission_classes = [
        PersonnelPermission,
    ]

    queryset = EmployeePromissoryNote.objects.all().order_by(
        "employee",
        "note_number",
    )

    serializer_class = EmployeePromissoryNoteSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if not (
            self.request.user.is_staff
            or self.request.user.is_superuser
        ):
            queryset = queryset.filter(
                employee__user=self.request.user
            )

        employee_id = self.request.query_params.get("employee")

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id
            )

        return queryset

    pagination_class = None
    
class EmployeeDocumentViewSet(viewsets.ModelViewSet):

    permission_classes = [
        PersonnelPermission,
    ]

    queryset = EmployeeDocument.objects.all().order_by(
        "-uploaded_at",
    )

    serializer_class = EmployeeDocumentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if not (
            self.request.user.is_staff
            or self.request.user.is_superuser
        ):
            queryset = queryset.filter(
                employee__user=self.request.user
            )

        employee_id = self.request.query_params.get("employee")
        document_type = self.request.query_params.get("document_type")
        is_verified = self.request.query_params.get("is_verified")
        expiry_status = self.request.query_params.get("expiry_status")

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id
            )

        if document_type:
            queryset = queryset.filter(
                document_type=document_type
            )

        if is_verified is not None:
            if is_verified.lower() == "true":
                queryset = queryset.filter(is_verified=True)

            elif is_verified.lower() == "false":
                queryset = queryset.filter(is_verified=False)

        today = timezone.localdate()

        if expiry_status == "expired":
            queryset = queryset.filter(
                expiry_date__lt=today
            )

        elif expiry_status == "valid":
            queryset = queryset.filter(
                expiry_date__gte=today
            )

        elif expiry_status == "no_expiry":
            queryset = queryset.filter(
                expiry_date__isnull=True
            )

        return queryset
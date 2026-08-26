from decimal import Decimal

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.audit.services import AuditService
from apps.payroll.models import EmployeeSalary, PayrollDeduction
from apps.payroll.serializers import (
    EmployeeSalarySerializer,
    PayrollDeductionSerializer,
)
from apps.payroll.services import PayrollCalculator


class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    """
    API مدیریت حقوق و مزایای پرسنل.
    """

    queryset = (
        EmployeeSalary.objects
        .select_related("employee")
        .prefetch_related(
            "employee__children",
            "deductions",
        )
        .all()
        .order_by("-year", "-month", "-id")
    )

    serializer_class = EmployeeSalarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        employee_id = self.request.query_params.get("employee")
        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")

        if employee_id:
            queryset = queryset.filter(
                employee_id=employee_id
            )

        if year:
            queryset = queryset.filter(
                year=year
            )

        if month:
            queryset = queryset.filter(
                month=month
            )

        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()

        AuditService.create(
            actor=self.request.user,
            instance=instance,
            request=self.request,
        )

    def perform_update(self, serializer):
        old_instance = EmployeeSalary.objects.get(
            pk=serializer.instance.pk
        )

        instance = serializer.save()

        changes = {}

        fields = [
            "employee_id",
            "year",
            "month",
            "monthly_wage",
            "worker_food_allowance",
            "housing_allowance",
            "child_allowance",
            "marriage_allowance",
            "notes",
        ]

        for field in fields:
            old_value = getattr(
                old_instance,
                field,
            )

            new_value = getattr(
                instance,
                field,
            )

            if old_value != new_value:
                changes[field] = {
                    "old": old_value,
                    "new": new_value,
                }

        if changes:
            AuditService.update(
                actor=self.request.user,
                instance=instance,
                request=self.request,
                changes=changes,
            )

    def perform_destroy(self, instance):
        AuditService.delete(
            actor=self.request.user,
            instance=instance,
            request=self.request,
        )

        instance.delete()

    @action(
        detail=True,
        methods=["get"],
        url_path="calculate",
    )
    def calculate(self, request, pk=None):
        """
        محاسبه کامل حقوق یک رکورد Salary.
        """

        salary = self.get_object()

        result = PayrollCalculator.calculate(
            salary.employee,
            salary,
        )

        data = {
            "salary_id": salary.id,
            "employee": salary.employee_id,
            "period": {
                "year": salary.year,
                "month": salary.month,
            },
            "earnings": {
                "monthly_wage": result["monthly_wage"],
                "worker_food_allowance": (
                    result["worker_food_allowance"]
                ),
                "housing_allowance": (
                    result["housing_allowance"]
                ),
                "marriage_allowance": (
                    result["marriage_allowance"]
                ),
                "child_allowance": (
                    result["child_allowance"]
                ),
                "gross_earnings": (
                    result["gross_earnings"]
                ),
            },
            "children": {
                "eligible_count": (
                    result["eligible_children_count"]
                ),
                "allowance_per_child": (
                    result["child_allowance_per_child"]
                ),
            },
            "deductions": {
                "insurance": result["insurance"],
                "tax": result["tax"],
                "advance": result["advance"],
                "loan": result["loan"],
                "absence": result["absence"],
                "other": result["other"],
                "total_deductions": (
                    result["total_deductions"]
                ),
            },
            "net_salary": result["net_salary"],
        }

        return Response(
            data,
            status=status.HTTP_200_OK,
        )

    pagination_class = None


class PayrollDeductionViewSet(viewsets.ModelViewSet):
    queryset = (
        PayrollDeduction.objects
        .select_related(
            "salary",
            "salary__employee",
        )
        .all()
        .order_by("-created_at", "-id")
    )

    serializer_class = PayrollDeductionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        salary_id = self.request.query_params.get("salary")
        deduction_type = self.request.query_params.get(
            "deduction_type"
        )

        if salary_id:
            queryset = queryset.filter(
                salary_id=salary_id
            )

        if deduction_type:
            queryset = queryset.filter(
                deduction_type=deduction_type
            )

        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()

        AuditService.create(
            actor=self.request.user,
            instance=instance,
            request=self.request,
        )

    def perform_update(self, serializer):
        old_instance = PayrollDeduction.objects.get(
            pk=serializer.instance.pk
        )

        instance = serializer.save()

        fields = [
            "salary_id",
            "deduction_type",
            "amount",
            "description",
        ]

        changes = {}

        for field in fields:
            old_value = getattr(old_instance, field)
            new_value = getattr(instance, field)

            if old_value != new_value:
                if isinstance(old_value, Decimal):
                    old_value = str(old_value)

                if isinstance(new_value, Decimal):
                    new_value = str(new_value)

                changes[field] = {
                    "old": old_value,
                    "new": new_value,
                }

        if changes:
            AuditService.update(
                actor=self.request.user,
                instance=instance,
                request=self.request,
                changes=changes,
            )

    def perform_destroy(self, instance):
        AuditService.delete(
            actor=self.request.user,
            instance=instance,
            request=self.request,
        )

        instance.delete()

    pagination_class = None
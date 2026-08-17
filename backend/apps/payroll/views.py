from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

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
    permission_classes = [AllowAny]

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


class PayrollDeductionViewSet(viewsets.ModelViewSet):
    """
    API مدیریت کسورات حقوق.
    """

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
    permission_classes = [AllowAny]

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
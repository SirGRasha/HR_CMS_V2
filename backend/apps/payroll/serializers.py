from rest_framework import serializers

from apps.payroll.models import (
    EmployeeSalary,
    PayrollDeduction,
)
from apps.payroll.services import PayrollCalculator


class EmployeeSalarySerializer(serializers.ModelSerializer):
    eligible_children_count = serializers.SerializerMethodField()
    daily_wage = serializers.SerializerMethodField()
    child_allowance_per_child = serializers.SerializerMethodField()
    calculated_child_allowance = serializers.SerializerMethodField()
    total_eligible_benefits = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeSalary
        fields = [
            "id",
            "employee",
            "year",
            "month",
            "monthly_wage",
            "worker_food_allowance",
            "housing_allowance",
            "marriage_allowance",
            "notes",
            "eligible_children_count",
            "daily_wage",
            "child_allowance_per_child",
            "calculated_child_allowance",
            "total_eligible_benefits",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "eligible_children_count",
            "daily_wage",
            "child_allowance_per_child",
            "calculated_child_allowance",
            "total_eligible_benefits",
            "created_at",
            "updated_at",
        ]

    def _calculate(self, obj):
        return PayrollCalculator.calculate(
            obj.employee,
            obj,
        )

    def get_eligible_children_count(self, obj):
        return self._calculate(obj)["eligible_children_count"]

    def get_daily_wage(self, obj):
        return self._calculate(obj)["daily_wage"]

    def get_child_allowance_per_child(self, obj):
        return self._calculate(obj)["child_allowance_per_child"]

    def get_calculated_child_allowance(self, obj):
        return self._calculate(obj)["child_allowance"]

    def get_total_eligible_benefits(self, obj):
        return self._calculate(obj)["total_eligible_benefits"]


class PayrollDeductionSerializer(serializers.ModelSerializer):
    deduction_type_display = serializers.CharField(
        source="get_deduction_type_display",
        read_only=True,
    )

    class Meta:
        model = PayrollDeduction
        fields = [
            "id",
            "salary",
            "deduction_type",
            "deduction_type_display",
            "amount",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "deduction_type_display",
            "created_at",
            "updated_at",
        ]
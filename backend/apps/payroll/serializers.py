from django.db import transaction
from rest_framework import serializers

from apps.payroll.models import (
    EmployeeSalary,
    PayrollBonus,
    PayrollDeduction,
)
from apps.payroll.services import PayrollCalculator


# ============================================================
# Bonus Serializers
# ============================================================

class PayrollBonusSerializer(serializers.ModelSerializer):
    """
    Serializer مستقل پاداش.

    برای endpoint مستقل:
    /api/payroll/bonuses/

    در این حالت salary باید توسط API دریافت شود.
    """

    class Meta:
        model = PayrollBonus
        fields = [
            "id",
            "salary",
            "title",
            "amount",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class PayrollBonusNestedSerializer(serializers.ModelSerializer):
    """
    Serializer پاداش در فرم یکپارچه حقوق.

    در این حالت salary از EmployeeSalary والد
    به صورت خودکار تعیین می‌شود.
    """

    class Meta:
        model = PayrollBonus
        fields = [
            "id",
            "title",
            "amount",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# ============================================================
# Deduction Serializers
# ============================================================

class PayrollDeductionSerializer(serializers.ModelSerializer):
    """
    Serializer مستقل کسورات.

    برای endpoint مستقل:
    /api/payroll/deductions/

    در این حالت salary باید توسط API دریافت شود.
    """

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


class PayrollDeductionNestedSerializer(serializers.ModelSerializer):
    """
    Serializer کسورات در فرم یکپارچه حقوق.

    در این حالت salary از EmployeeSalary والد
    به صورت خودکار تعیین می‌شود.
    """

    deduction_type_display = serializers.CharField(
        source="get_deduction_type_display",
        read_only=True,
    )

    class Meta:
        model = PayrollDeduction
        fields = [
            "id",
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


# ============================================================
# Employee Salary Serializer
# ============================================================

class EmployeeSalarySerializer(serializers.ModelSerializer):
    """
    Serializer اصلی حقوق و مزایا.

    اطلاعات فرزندان مستقیماً از Employee خوانده می‌شود
    و حق اولاد توسط PayrollCalculator به صورت خودکار
    محاسبه می‌شود.

    پاداش‌ها و کسورات می‌توانند همراه رکورد حقوق
    ایجاد یا ویرایش شوند.
    """

    eligible_children_count = serializers.SerializerMethodField()
    daily_wage = serializers.SerializerMethodField()
    child_allowance_per_child = serializers.SerializerMethodField()
    calculated_child_allowance = serializers.SerializerMethodField()
    total_eligible_benefits = serializers.SerializerMethodField()

    bonuses = PayrollBonusNestedSerializer(
        many=True,
        required=False,
    )

    deductions = PayrollDeductionNestedSerializer(
        many=True,
        required=False,
    )

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

            # محاسبات خودکار
            "eligible_children_count",
            "daily_wage",
            "child_allowance_per_child",
            "calculated_child_allowance",
            "total_eligible_benefits",

            # حقوق تکمیلی
            "bonuses",
            "deductions",

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

    # ========================================================
    # Payroll Calculation
    # ========================================================

    def _calculate(self, obj):
        if not hasattr(
            self,
            "_payroll_calculation_cache",
        ):
            self._payroll_calculation_cache = {}

        cache_key = obj.pk

        if cache_key not in self._payroll_calculation_cache:
            self._payroll_calculation_cache[cache_key] = (
                PayrollCalculator.calculate(
                    obj.employee,
                    obj,
                )
            )

        return self._payroll_calculation_cache[cache_key]

    def get_eligible_children_count(self, obj):
        return self._calculate(obj)[
            "eligible_children_count"
        ]

    def get_daily_wage(self, obj):
        return self._calculate(obj)[
            "daily_wage"
        ]

    def get_child_allowance_per_child(self, obj):
        return self._calculate(obj)[
            "child_allowance_per_child"
        ]

    def get_calculated_child_allowance(self, obj):
        return self._calculate(obj)[
            "child_allowance"
        ]

    def get_total_eligible_benefits(self, obj):
        return self._calculate(obj)[
            "total_eligible_benefits"
        ]

    # ========================================================
    # Create
    # ========================================================

    @transaction.atomic
    def create(self, validated_data):
        bonuses_data = validated_data.pop(
            "bonuses",
            [],
        )

        deductions_data = validated_data.pop(
            "deductions",
            [],
        )

        salary = EmployeeSalary.objects.create(
            **validated_data
        )

        for bonus_data in bonuses_data:
            PayrollBonus.objects.create(
                salary=salary,
                **bonus_data,
            )

        for deduction_data in deductions_data:
            PayrollDeduction.objects.create(
                salary=salary,
                **deduction_data,
            )

        return salary

    # ========================================================
    # Update
    # ========================================================

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):
        bonuses_data = validated_data.pop(
            "bonuses",
            None,
        )

        deductions_data = validated_data.pop(
            "deductions",
            None,
        )

        instance = super().update(
            instance,
            validated_data,
        )

        if bonuses_data is not None:
            instance.bonuses.all().delete()

            for bonus_data in bonuses_data:
                PayrollBonus.objects.create(
                    salary=instance,
                    **bonus_data,
                )

        if deductions_data is not None:
            instance.deductions.all().delete()

            for deduction_data in deductions_data:
                PayrollDeduction.objects.create(
                    salary=instance,
                    **deduction_data,
                )

        return instance
from decimal import Decimal

from django.utils import timezone

from apps.payroll.services.child_allowance import (
    calculate_child_allowance,
)
from apps.payroll.services.deduction_calculator import (
    DeductionCalculator,
)


class PayrollCalculator:
    """
    موتور اصلی محاسبه حقوق و مزایای پرسنل.

    این کلاس مسئول orchestration است و منطق جزئی
    حق اولاد و کسورات را به سرویس‌های تخصصی واگذار می‌کند.
    """

    @staticmethod
    def calculate(employee, salary):
        """
        محاسبه کامل حقوق، مزایا، کسورات و حقوق خالص.
        """

        monthly_wage = Decimal(
            str(salary.monthly_wage)
        )

        worker_food_allowance = Decimal(
            str(salary.worker_food_allowance)
        )

        housing_allowance = Decimal(
            str(salary.housing_allowance)
        )

        marriage_allowance = Decimal(
            str(salary.marriage_allowance)
        )

        # --------------------------------------------------
        # Child allowance
        # --------------------------------------------------

        child_result = calculate_child_allowance(
            employee=employee,
            reference_date=timezone.localdate(),
            monthly_wage=monthly_wage,
        )

        eligible_children_count = (
            child_result["eligible_children_count"]
        )

        daily_wage = child_result["daily_wage"]

        child_allowance_per_child = (
            child_result["allowance_per_child"]
        )

        child_allowance = (
            child_result["total_child_allowance"]
        )

        # --------------------------------------------------
        # Earnings
        # --------------------------------------------------

        gross_earnings = (
            monthly_wage
            + worker_food_allowance
            + housing_allowance
            + marriage_allowance
            + child_allowance
        )

        total_eligible_benefits = gross_earnings

        # --------------------------------------------------
        # Deductions
        # --------------------------------------------------

        deduction_result = (
            DeductionCalculator.calculate(salary)
        )

        deductions = deduction_result["deductions"]

        total_deductions = (
            deduction_result["total_deductions"]
        )

        # --------------------------------------------------
        # Net salary
        # --------------------------------------------------

        net_salary = (
            gross_earnings - total_deductions
        )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        return {
            "monthly_wage": monthly_wage,
            "worker_food_allowance": (
                worker_food_allowance
            ),
            "housing_allowance": housing_allowance,
            "marriage_allowance": marriage_allowance,
            "daily_wage": daily_wage,
            "eligible_children_count": (
                eligible_children_count
            ),
            "child_allowance_per_child": (
                child_allowance_per_child
            ),
            "child_allowance": child_allowance,
            "total_eligible_benefits": (
                total_eligible_benefits
            ),
            "gross_earnings": gross_earnings,
            "insurance": deductions["insurance"],
            "tax": deductions["tax"],
            "advance": deductions["advance"],
            "loan": deductions["loan"],
            "absence": deductions["absence"],
            "other": deductions["other"],
            "total_deductions": total_deductions,
            "net_salary": net_salary,
        }
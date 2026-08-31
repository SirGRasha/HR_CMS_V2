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

    مسئولیت این کلاس:
    - محاسبه حقوق پایه
    - محاسبه مزایای ثابت
    - محاسبه خودکار حق اولاد
    - محاسبه مجموع پاداش‌ها
    - محاسبه کسورات
    - محاسبه حقوق ناخالص
    - محاسبه حقوق خالص
    """

    @staticmethod
    def calculate(employee, salary):
        """
        محاسبه کامل حقوق، مزایا، پاداش‌ها،
        کسورات و حقوق خالص.
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
        # Bonuses
        # --------------------------------------------------

        total_bonuses = Decimal("0")

        for bonus in salary.bonuses.all():
            total_bonuses += Decimal(
                str(bonus.amount)
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
            + total_bonuses
        )

        total_eligible_benefits = (
            monthly_wage
            + worker_food_allowance
            + housing_allowance
            + marriage_allowance
            + child_allowance
        )

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

            "housing_allowance": (
                housing_allowance
            ),

            "marriage_allowance": (
                marriage_allowance
            ),

            # Child
            "daily_wage": daily_wage,

            "eligible_children_count": (
                eligible_children_count
            ),

            "child_allowance_per_child": (
                child_allowance_per_child
            ),

            "child_allowance": (
                child_allowance
            ),

            # Bonuses
            "total_bonuses": total_bonuses,

            # Earnings
            "total_eligible_benefits": (
                total_eligible_benefits
            ),

            "gross_earnings": (
                gross_earnings
            ),

            # Deductions
            "insurance": deductions["insurance"],

            "tax": deductions["tax"],

            "advance": deductions["advance"],

            "loan": deductions["loan"],

            "absence": deductions["absence"],

            "other": deductions["other"],

            "total_deductions": (
                total_deductions
            ),

            # Net
            "net_salary": net_salary,
        }
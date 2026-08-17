from decimal import Decimal

from apps.payroll.services.child_allowance import (
    calculate_child_allowance,
)


class PayrollCalculator:
    """
    موتور محاسبه حقوق و مزایای پرسنل.

    منطق مربوط به حق اولاد در child_allowance.py
    نگهداری می‌شود تا قوانین محاسباتی در یک محل متمرکز باشند.
    """

    CHILD_ALLOWANCE_DAYS = Decimal("3")
    DAYS_IN_MONTH = Decimal("30")

    @classmethod
    def calculate_child_allowance(cls, employee, monthly_wage):
        """
        محاسبه حق اولاد بر اساس فرزندان واجد شرایط.

        این متد برای حفظ API داخلی قبلی PayrollCalculator
        نگه داشته شده و محاسبه اصلی را به سرویس child_allowance
        واگذار می‌کند.
        """

        from django.utils import timezone

        result = calculate_child_allowance(
            employee=employee,
            reference_date=timezone.localdate(),
            monthly_wage=monthly_wage,
        )

        return result["total_child_allowance"]

    @classmethod
    def calculate_total_compensable(
        cls,
        monthly_wage,
        worker_food_allowance,
        housing_allowance,
        child_allowance,
        marriage_allowance,
    ):
        """
        محاسبه مجموع حقوق و مزایای مشمول.
        """

        return (
            Decimal(monthly_wage)
            + Decimal(worker_food_allowance)
            + Decimal(housing_allowance)
            + Decimal(child_allowance)
            + Decimal(marriage_allowance)
        )

    @classmethod
    def calculate(cls, employee, salary):
        """
        محاسبه کامل حقوق و مزایای یک رکورد حقوق.
        """

        eligible_children = cls.get_eligible_children(employee)

        daily_wage = (
            Decimal(salary.monthly_wage)
            / Decimal("30")
        )

        child_allowance_per_child = (
            daily_wage
            * cls.CHILD_ALLOWANCE_DAYS
        )

        child_allowance = (
            child_allowance_per_child
            * Decimal(len(eligible_children))
        )

        total_eligible_benefits = cls.calculate_total_compensable(
            monthly_wage=salary.monthly_wage,
            worker_food_allowance=salary.worker_food_allowance,
            housing_allowance=salary.housing_allowance,
            child_allowance=child_allowance,
            marriage_allowance=salary.marriage_allowance,
        )

        return {
            "eligible_children_count": len(
                eligible_children
            ),
            "daily_wage": daily_wage,
            "child_allowance_per_child": (
                child_allowance_per_child
            ),
            "child_allowance": child_allowance,
            "total_eligible_benefits": (
                total_eligible_benefits
            ),
        }
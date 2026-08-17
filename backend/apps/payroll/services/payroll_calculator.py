from datetime import date
from decimal import Decimal


class PayrollCalculator:
    """
    موتور محاسبه حقوق و مزایای پرسنل.
    """

    @staticmethod
    def calculate_employee_age(birth_date):
        """
        محاسبه سن دقیق بر اساس تاریخ میلادی ذخیره‌شده در دیتابیس.
        """
        if not birth_date:
            return None

        today = date.today()

        age = today.year - birth_date.year

        if (today.month, today.day) < (
            birth_date.month,
            birth_date.day,
        ):
            age -= 1

        return age

    @staticmethod
    def is_child_eligible(child):
        """
        تعیین واجد شرایط بودن فرزند برای حق اولاد.

        قوانین:
        - زیر 18 سال: واجد شرایط
        - 18 سال و بالاتر + گواهی اشتغال به تحصیل: واجد شرایط
        - 18 سال و بالاتر بدون گواهی: غیرواجد شرایط
        """

        if not child.is_active:
            return False

        age = PayrollCalculator.calculate_employee_age(
            child.birth_date
        )

        if age is None:
            return False

        if age < 18:
            return True

        return bool(child.education_certificate)

    @staticmethod
    def calculate(employee, salary):
        """
        محاسبه کامل حقوق، مزایا، کسورات و حقوق خالص.
        """

        monthly_wage = Decimal(salary.monthly_wage)
        worker_food_allowance = Decimal(
            salary.worker_food_allowance
        )
        housing_allowance = Decimal(
            salary.housing_allowance
        )
        marriage_allowance = Decimal(
            salary.marriage_allowance
        )

        # --------------------------------------------------
        # Child allowance
        # --------------------------------------------------

        eligible_children_count = 0

        children = employee.children.filter(
            is_active=True
        )

        for child in children:
            if PayrollCalculator.is_child_eligible(child):
                eligible_children_count += 1

        # مزد روزانه بر مبنای 30 روز
        daily_wage = (
            monthly_wage / Decimal("30")
        )

        # حق اولاد هر فرزند = 3 روز مزد
        child_allowance_per_child = (
            daily_wage * Decimal("3")
        )

        # حق اولاد کل
        child_allowance = (
            child_allowance_per_child
            * eligible_children_count
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

        deduction_totals = {
            "insurance": Decimal("0"),
            "tax": Decimal("0"),
            "advance": Decimal("0"),
            "loan": Decimal("0"),
            "absence": Decimal("0"),
            "other": Decimal("0"),
        }

        deductions = salary.deductions.all()

        for deduction in deductions:
            deduction_type = deduction.deduction_type

            if deduction_type in deduction_totals:
                deduction_totals[deduction_type] += Decimal(
                    deduction.amount
                )

        total_deductions = sum(
            deduction_totals.values(),
            Decimal("0"),
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
            "worker_food_allowance": worker_food_allowance,
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

            "insurance": deduction_totals["insurance"],
            "tax": deduction_totals["tax"],
            "advance": deduction_totals["advance"],
            "loan": deduction_totals["loan"],
            "absence": deduction_totals["absence"],
            "other": deduction_totals["other"],

            "total_deductions": total_deductions,
            "net_salary": net_salary,
        }
from decimal import Decimal


class DeductionCalculator:
    """
    موتور محاسبه کسورات حقوق.

    مسئولیت:
    - جمع کردن کسورات ثبت شده
    - تفکیک بر اساس نوع کسری
    - آماده سازی اطلاعات برای محاسبه حقوق خالص
    """

    DEDUCTION_TYPES = [
        "insurance",
        "tax",
        "advance",
        "loan",
        "absence",
        "other",
    ]

    @classmethod
    def calculate(cls, salary):
        """
        محاسبه تمام کسورات یک رکورد حقوق.
        """

        deductions = {
            deduction_type: Decimal("0")
            for deduction_type in cls.DEDUCTION_TYPES
        }

        total_deductions = Decimal("0")

        for deduction in salary.deductions.all():

            amount = Decimal(
                deduction.amount
            )

            deductions[
                deduction.deduction_type
            ] += amount

            total_deductions += amount

        return {
            "deductions": deductions,
            "total_deductions": total_deductions,
        }
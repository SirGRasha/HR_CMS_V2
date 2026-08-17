from decimal import Decimal


CHILD_ALLOWANCE_DAYS = Decimal("3")
DAYS_IN_MONTH = Decimal("30")


def calculate_age(birth_date, reference_date):
    """
    محاسبه سن دقیق در تاریخ مرجع.
    """

    if birth_date > reference_date:
        return 0

    age = reference_date.year - birth_date.year

    if (
        reference_date.month,
        reference_date.day,
    ) < (
        birth_date.month,
        birth_date.day,
    ):
        age -= 1

    return age


def is_child_eligible(child, reference_date):
    """
    تعیین مشمول بودن فرزند برای حق اولاد.

    زیر 18 سال:
        مشمول

    18 سال و بالاتر:
        فقط در صورت داشتن گواهی اشتغال به تحصیل مشمول.
    """

    age = calculate_age(
        child.birth_date,
        reference_date,
    )

    if age < 18:
        return True

    return child.education_certificate


def calculate_child_allowance(
    employee,
    reference_date,
    monthly_wage,
):
    """
    محاسبه حق اولاد.

    مزد ماهیانه بر مبنای 30 روز محاسبه می‌شود.
    """

    monthly_wage = Decimal(str(monthly_wage))

    daily_wage = (
        monthly_wage / DAYS_IN_MONTH
    )

    allowance_per_child = (
        daily_wage * CHILD_ALLOWANCE_DAYS
    )

    children = employee.children.filter(
        is_active=True
    )

    eligible_children = []
    ineligible_children = []

    for child in children:

        if is_child_eligible(
            child,
            reference_date,
        ):
            eligible_children.append(child)
        else:
            ineligible_children.append(child)

    total_allowance = (
        allowance_per_child
        * Decimal(len(eligible_children))
    )

    return {
        "eligible_children": eligible_children,
        "ineligible_children": ineligible_children,
        "eligible_children_count": len(
            eligible_children
        ),
        "ineligible_children_count": len(
            ineligible_children
        ),
        "daily_wage": daily_wage,
        "allowance_per_child": allowance_per_child,
        "total_child_allowance": total_allowance,
    }
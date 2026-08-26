from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.personnel.models import Employee, EmployeeChild
from apps.payroll.services.child_allowance import (
    calculate_age,
    calculate_child_allowance,
    is_child_eligible,
)


class ChildAllowanceTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="PAY-TEST-001",
            first_name="رضا",
            last_name="تست",
            gender="male",
            employee_group="administrative",
            department="فناوری اطلاعات",
            job_title="کارشناس IT",
            start_date=date(2026, 1, 1),
            insurance_date=date(2026, 1, 1),
            insurance_number="1234567890",
            birth_date=date(1995, 1, 1),
            national_id="0012345678",
            birth_certificate_number="123456",
            father_name="نام پدر",
            education_level="کارشناسی",
            field_of_study="مهندسی کامپیوتر",
            student_number="",
            military_status="exemption",
            marital_status="married",
            child_count=3,
            landline_phone="02112345678",
            residence_area="تهران",
            address="آدرس تست",
            transportation_status="personal",
            transportation_description="",
            contract_title="قرارداد تست",
            contract_position="کارشناس IT",
            notes="",
            is_active=True,
        )

    def test_age_calculation(self):

        age = calculate_age(
            date(2015, 8, 10),
            date(2026, 8, 14),
        )

        self.assertEqual(age, 11)

    def test_child_under_18_is_eligible(self):

        child = EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند زیر ۱۸ سال",
            birth_date=date(2015, 8, 10),
            education_certificate=False,
            is_active=True,
        )

        result = is_child_eligible(
            child,
            date(2026, 8, 14),
        )

        self.assertTrue(result)

    def test_child_over_18_with_certificate_is_eligible(self):

        child = EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند بالای ۱۸ با گواهی",
            birth_date=date(2005, 1, 1),
            education_certificate=True,
            is_active=True,
        )

        result = is_child_eligible(
            child,
            date(2026, 8, 14),
        )

        self.assertTrue(result)

    def test_child_over_18_without_certificate_is_not_eligible(self):

        child = EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند بالای ۱۸ بدون گواهی",
            birth_date=date(2005, 1, 1),
            education_certificate=False,
            is_active=True,
        )

        result = is_child_eligible(
            child,
            date(2026, 8, 14),
        )

        self.assertFalse(result)

    def test_child_exactly_18_without_certificate_is_not_eligible(self):
        child = EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند دقیقاً ۱۸ ساله بدون گواهی",
            birth_date=date(2008, 8, 14),
            education_certificate=False,
            is_active=True,
        )

        result = is_child_eligible(
            child,
            date(2026, 8, 14),
        )

        self.assertFalse(result)

    def test_child_exactly_18_with_certificate_is_eligible(self):
        child = EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند دقیقاً ۱۸ ساله با گواهی",
            birth_date=date(2008, 8, 14),
            education_certificate=True,
            is_active=True,
        )

        result = is_child_eligible(
            child,
            date(2026, 8, 14),
        )

        self.assertTrue(result)

    def test_child_one_day_before_18_is_eligible(self):
        child = EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند یک روز مانده به ۱۸ سالگی",
            birth_date=date(2008, 8, 15),
            education_certificate=False,
            is_active=True,
        )

        result = is_child_eligible(
            child,
            date(2026, 8, 14),
        )

        self.assertTrue(result)

    def test_inactive_child_is_not_eligible_for_allowance(self):
        child = EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند غیرفعال",
            birth_date=date(2015, 1, 1),
            education_certificate=False,
            is_active=False,
        )

        result = calculate_child_allowance(
            employee=self.employee,
            reference_date=date(2026, 8, 14),
            monthly_wage=Decimal("300000000"),
        )

        self.assertFalse(
            is_child_eligible(
                child,
                date(2026, 8, 14),
            )
        )

        self.assertNotIn(
            child,
            result["eligible_children"],
        )

    def test_future_birth_date_has_zero_age(self):
        age = calculate_age(
            date(2030, 1, 1),
            date(2026, 8, 14),
        )

        self.assertEqual(age, 0)

    def test_child_allowance_calculation(self):

        EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند اول",
            birth_date=date(2015, 1, 1),
            education_certificate=False,
            is_active=True,
        )

        EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند دوم",
            birth_date=date(2005, 1, 1),
            education_certificate=True,
            is_active=True,
        )

        EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند سوم",
            birth_date=date(2004, 1, 1),
            education_certificate=False,
            is_active=True,
        )

        result = calculate_child_allowance(
            employee=self.employee,
            reference_date=date(2026, 8, 14),
            monthly_wage=Decimal("300000000"),
        )

        self.assertEqual(
            result["eligible_children_count"],
            2,
        )

        self.assertEqual(
            result["ineligible_children_count"],
            1,
        )

        self.assertEqual(
            result["daily_wage"],
            Decimal("10000000"),
        )

        self.assertEqual(
            result["allowance_per_child"],
            Decimal("30000000"),
        )

        self.assertEqual(
            result["total_child_allowance"],
            Decimal("60000000"),
        )
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from apps.accounts.models import User
from apps.personnel.models import Employee, EmployeeChild
from apps.payroll.models import EmployeeSalary, PayrollDeduction
from apps.payroll.services import PayrollCalculator


class PayrollCalculatorTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="TEST-001",
            first_name="رضا",
            last_name="تست",
            gender="male",
            employee_group="administrative",
            marital_status="married",
            national_id="0012345678",
            child_count=2,
        )

        EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند اول",
            birth_date=date(2015, 1, 1),
            education_certificate=False,
        )

        EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند دوم",
            birth_date=date(1995, 1, 1),
            education_certificate=False,
        )

        self.salary = EmployeeSalary.objects.create(
            employee=self.employee,
            year=1405,
            month=5,
            monthly_wage=30000000,
            worker_food_allowance=5000000,
            housing_allowance=5000000,
            marriage_allowance=2000000,
        )

    def test_child_allowance_calculation(self):
        result = PayrollCalculator.calculate(
            self.employee,
            self.salary,
        )

        self.assertEqual(
            result["eligible_children_count"],
            1,
        )

        expected_child_allowance = (
            Decimal("30000000") / Decimal("30")
        ) * Decimal("3")

        self.assertEqual(
            result["child_allowance"],
            expected_child_allowance,
        )

    def test_daily_wage_calculation(self):
        result = PayrollCalculator.calculate(
            self.employee,
            self.salary,
        )

        self.assertEqual(
            result["daily_wage"],
            Decimal("1000000"),
        )

    def test_child_allowance_per_child_calculation(self):
        result = PayrollCalculator.calculate(
            self.employee,
            self.salary,
        )

        self.assertEqual(
            result["child_allowance_per_child"],
            Decimal("3000000"),
        )

    def test_total_eligible_benefits_calculation(self):
        result = PayrollCalculator.calculate(
            self.employee,
            self.salary,
        )

        expected = (
            Decimal("30000000")
            + Decimal("5000000")
            + Decimal("5000000")
            + Decimal("3000000")
            + Decimal("2000000")
        )

        self.assertEqual(
            result["total_eligible_benefits"],
            expected,
        )

    def test_no_eligible_children_means_zero_child_allowance(self):
        EmployeeChild.objects.all().delete()

        result = PayrollCalculator.calculate(
            self.employee,
            self.salary,
        )

        self.assertEqual(
            result["eligible_children_count"],
            0,
        )

        self.assertEqual(
            result["child_allowance"],
            Decimal("0"),
        )

        self.assertEqual(
            result["child_allowance_per_child"],
            Decimal("3000000"),
        )

    def test_multiple_eligible_children_calculation(self):
        EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند سوم",
            birth_date=date(2010, 1, 1),
            education_certificate=False,
        )

        result = PayrollCalculator.calculate(
            self.employee,
            self.salary,
        )

        self.assertEqual(
            result["eligible_children_count"],
            2,
        )

        self.assertEqual(
            result["child_allowance"],
            Decimal("6000000"),
        )


    def test_no_deductions_means_zero_total_deductions(self):
        result = PayrollCalculator.calculate(
            self.employee,
            self.salary,
        )

        self.assertEqual(
            result["total_deductions"],
            Decimal("0"),
        )

        self.assertEqual(
            result["insurance"],
            Decimal("0"),
        )

        self.assertEqual(
            result["tax"],
            Decimal("0"),
        )

    def test_deductions_are_calculated_by_type(self):
        PayrollDeduction.objects.create(
            salary=self.salary,
            deduction_type="insurance",
            amount=3000000,
        )

        PayrollDeduction.objects.create(
            salary=self.salary,
            deduction_type="tax",
            amount=1500000,
        )

        PayrollDeduction.objects.create(
            salary=self.salary,
            deduction_type="loan",
            amount=2000000,
        )

        result = PayrollCalculator.calculate(
            self.employee,
            self.salary,
        )

        self.assertEqual(
            result["insurance"],
            Decimal("3000000"),
        )

        self.assertEqual(
            result["tax"],
            Decimal("1500000"),
        )

        self.assertEqual(
            result["loan"],
            Decimal("2000000"),
        )

        self.assertEqual(
            result["total_deductions"],
            Decimal("6500000"),
        )

    def test_multiple_deductions_of_same_type_are_summed(self):
        PayrollDeduction.objects.create(
            salary=self.salary,
            deduction_type="loan",
            amount=2000000,
        )

        PayrollDeduction.objects.create(
            salary=self.salary,
            deduction_type="loan",
            amount=1500000,
        )

        result = PayrollCalculator.calculate(
            self.employee,
            self.salary,
        )

        self.assertEqual(
            result["loan"],
            Decimal("3500000"),
        )

        self.assertEqual(
            result["total_deductions"],
            Decimal("3500000"),
        )

    def test_net_salary_is_gross_minus_total_deductions(self):
        PayrollDeduction.objects.create(
            salary=self.salary,
            deduction_type="insurance",
            amount=3000000,
        )

        PayrollDeduction.objects.create(
            salary=self.salary,
            deduction_type="tax",
            amount=1500000,
        )

        result = PayrollCalculator.calculate(
            self.employee,
            self.salary,
        )

        expected_gross = (
            Decimal("30000000")
            + Decimal("5000000")
            + Decimal("5000000")
            + Decimal("3000000")
            + Decimal("2000000")
        )

        expected_deductions = (
            Decimal("3000000")
            + Decimal("1500000")
        )

        self.assertEqual(
            result["gross_earnings"],
            expected_gross,
        )

        self.assertEqual(
            result["total_deductions"],
            expected_deductions,
        )

        self.assertEqual(
            result["net_salary"],
            expected_gross - expected_deductions,
        )

class EmployeeSalaryAPITest(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="payroll_test",
            password="StrongPassword123",
        )

        self.client.force_authenticate(
            user=self.user
        )
        
        self.employee = Employee.objects.create(
            personnel_code="API-PAY-001",
            first_name="تست",
            last_name="حقوق",
            gender="male",
            employee_group="administrative",
            marital_status="married",
            national_id="0045678901",
            birth_date=date(1995, 1, 1),
            start_date=date(2020, 1, 1),
            insurance_date=date(2020, 2, 1),
        )

        self.other_employee = Employee.objects.create(
            personnel_code="API-PAY-002",
            first_name="تست",
            last_name="دوم",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0056789012",
            birth_date=date(1996, 1, 1),
            start_date=date(2021, 1, 1),
            insurance_date=date(2021, 2, 1),
        )

        EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند تست",
            birth_date=date(2015, 1, 1),
            education_certificate=False,
        )

    def create_salary(
        self,
        employee=None,
        year=1405,
        month=5,
        monthly_wage=30000000,
        worker_food_allowance=5000000,
        housing_allowance=5000000,
        marriage_allowance=2000000,
    ):
        if employee is None:
            employee = self.employee

        return EmployeeSalary.objects.create(
            employee=employee,
            year=year,
            month=month,
            monthly_wage=monthly_wage,
            worker_food_allowance=worker_food_allowance,
            housing_allowance=housing_allowance,
            marriage_allowance=marriage_allowance,
        )

    def test_list_salaries(self):
        self.create_salary()

        response = self.client.get(
            "/api/payroll/salaries/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_filter_salaries_by_employee(self):
        salary = self.create_salary(
            employee=self.employee,
        )

        self.create_salary(
            employee=self.other_employee,
            month=6,
        )

        response = self.client.get(
            "/api/payroll/salaries/",
            {
                "employee": self.employee.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            salary.id,
        )

    def test_filter_salaries_by_year(self):
        salary = self.create_salary(
            year=1405,
            month=5,
        )

        self.create_salary(
            year=1404,
            month=12,
        )

        response = self.client.get(
            "/api/payroll/salaries/",
            {
                "year": 1405,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            salary.id,
        )

    def test_filter_salaries_by_month(self):
        salary = self.create_salary(
            year=1405,
            month=5,
        )

        self.create_salary(
            year=1405,
            month=6,
        )

        response = self.client.get(
            "/api/payroll/salaries/",
            {
                "month": 5,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            salary.id,
        )

    def test_combined_salary_filters(self):
        target_salary = self.create_salary(
            employee=self.employee,
            year=1405,
            month=5,
        )

        self.create_salary(
            employee=self.employee,
            year=1405,
            month=6,
        )

        self.create_salary(
            employee=self.other_employee,
            year=1405,
            month=5,
        )

        self.create_salary(
            employee=self.employee,
            year=1404,
            month=5,
        )

        response = self.client.get(
            "/api/payroll/salaries/",
            {
                "employee": self.employee.id,
                "year": 1405,
                "month": 5,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]["id"],
            target_salary.id,
        )

    def test_create_salary(self):
        response = self.client.post(
            "/api/payroll/salaries/",
            {
                "employee": self.employee.id,
                "year": 1405,
                "month": 7,
                "monthly_wage": "30000000",
                "worker_food_allowance": "5000000",
                "housing_allowance": "5000000",
                "marriage_allowance": "2000000",
                "notes": "تست ایجاد حقوق",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertEqual(
            EmployeeSalary.objects.count(),
            1,
        )

        self.assertEqual(
            response.data["employee"],
            self.employee.id,
        )

        self.assertEqual(
            response.data["year"],
            1405,
        )

        self.assertEqual(
            response.data["month"],
            7,
        )

    def test_retrieve_salary(self):
        salary = self.create_salary()

        response = self.client.get(
            f"/api/payroll/salaries/{salary.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            salary.id,
        )

    def test_update_salary(self):
        salary = self.create_salary()

        response = self.client.patch(
            f"/api/payroll/salaries/{salary.id}/",
            {
                "monthly_wage": "35000000",
                "housing_allowance": "6000000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        salary.refresh_from_db()

        self.assertEqual(
            salary.monthly_wage,
            Decimal("35000000"),
        )

        self.assertEqual(
            salary.housing_allowance,
            Decimal("6000000"),
        )

    def test_delete_salary(self):
        salary = self.create_salary()

        response = self.client.delete(
            f"/api/payroll/salaries/{salary.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            EmployeeSalary.objects.filter(
                id=salary.id
            ).exists()
        )

    def test_duplicate_salary_period_is_rejected(self):
        self.create_salary(
            employee=self.employee,
            year=1405,
            month=5,
        )

        response = self.client.post(
            "/api/payroll/salaries/",
            {
                "employee": self.employee.id,
                "year": 1405,
                "month": 5,
                "monthly_wage": "40000000",
                "worker_food_allowance": "5000000",
                "housing_allowance": "5000000",
                "marriage_allowance": "2000000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_same_period_for_different_employee_is_allowed(self):
        self.create_salary(
            employee=self.employee,
            year=1405,
            month=5,
        )

        response = self.client.post(
            "/api/payroll/salaries/",
            {
                "employee": self.other_employee.id,
                "year": 1405,
                "month": 5,
                "monthly_wage": "40000000",
                "worker_food_allowance": "5000000",
                "housing_allowance": "5000000",
                "marriage_allowance": "2000000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertEqual(
            EmployeeSalary.objects.count(),
            2,
        )

    def test_same_employee_different_month_is_allowed(self):
        self.create_salary(
            employee=self.employee,
            year=1405,
            month=5,
        )

        response = self.client.post(
            "/api/payroll/salaries/",
            {
                "employee": self.employee.id,
                "year": 1405,
                "month": 6,
                "monthly_wage": "40000000",
                "worker_food_allowance": "5000000",
                "housing_allowance": "5000000",
                "marriage_allowance": "2000000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertEqual(
            EmployeeSalary.objects.count(),
            2,
        )

    def test_create_salary_with_invalid_month_is_rejected(self):
        response = self.client.post(
            "/api/payroll/salaries/",
            {
                "employee": self.employee.id,
                "year": 1405,
                "month": 13,
                "monthly_wage": "30000000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

    def test_create_salary_with_negative_wage_is_rejected(self):
        response = self.client.post(
            "/api/payroll/salaries/",
            {
                "employee": self.employee.id,
                "year": 1405,
                "month": 7,
                "monthly_wage": "-1000000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

    def test_salary_response_contains_calculated_fields(self):
        salary = self.create_salary(
            year=1405,
            month=8,
        )

        response = self.client.get(
            f"/api/payroll/salaries/{salary.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "eligible_children_count",
            response.data,
        )

        self.assertIn(
            "daily_wage",
            response.data,
        )

        self.assertIn(
            "child_allowance_per_child",
            response.data,
        )

        self.assertIn(
            "calculated_child_allowance",
            response.data,
        )

        self.assertIn(
            "total_eligible_benefits",
            response.data,
        )
    def test_calculate_salary_endpoint(self):
        salary = self.create_salary(
            year=1405,
            month=8,
        )

        PayrollDeduction.objects.create(
            salary=salary,
            deduction_type="insurance",
            amount=3000000,
        )

        PayrollDeduction.objects.create(
            salary=salary,
            deduction_type="tax",
            amount=1500000,
        )

        PayrollDeduction.objects.create(
            salary=salary,
            deduction_type="loan",
            amount=2000000,
        )

        response = self.client.get(
            f"/api/payroll/salaries/{salary.id}/calculate/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        self.assertEqual(
            response.data["salary_id"],
            salary.id,
        )

        self.assertEqual(
            response.data["employee"],
            self.employee.id,
        )

        self.assertEqual(
            response.data["period"]["year"],
            1405,
        )

        self.assertEqual(
            response.data["period"]["month"],
            8,
        )

        self.assertEqual(
            Decimal(
                response.data["earnings"]["gross_earnings"]
            ),
            Decimal("45000000"),
        )

        self.assertEqual(
            Decimal(
                response.data["deductions"]["insurance"]
            ),
            Decimal("3000000"),
        )

        self.assertEqual(
            Decimal(
                response.data["deductions"]["tax"]
            ),
            Decimal("1500000"),
        )

        self.assertEqual(
            Decimal(
                response.data["deductions"]["loan"]
            ),
            Decimal("2000000"),
        )

        self.assertEqual(
            Decimal(
                response.data["deductions"]["total_deductions"]
            ),
            Decimal("6500000"),
        )

        self.assertEqual(
            Decimal(response.data["net_salary"]),
            Decimal("38500000"),
        )

    @patch(
        "apps.payroll.serializers.PayrollCalculator.calculate"
    )
    def test_salary_serializer_calculates_payroll_only_once(
        self,
        mock_calculate,
    ):
        salary = self.create_salary(
            year=1405,
            month=8,
        )

        mock_calculate.return_value = {
            "eligible_children_count": 1,
            "daily_wage": Decimal("1000000"),
            "child_allowance_per_child": Decimal("3000000"),
            "child_allowance": Decimal("3000000"),
            "total_eligible_benefits": Decimal("45000000"),
        }

        response = self.client.get(
            f"/api/payroll/salaries/{salary.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            mock_calculate.call_count,
            1,
        )



class EmployeeSalaryValidationTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="VAL-001",
            first_name="رضا",
            last_name="تست",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0023456789",
        )

    def test_valid_salary_data(self):
        salary = EmployeeSalary(
            employee=self.employee,
            year=1405,
            month=6,
            monthly_wage=30000000,
            worker_food_allowance=5000000,
            housing_allowance=5000000,
            child_allowance=0,
            marriage_allowance=0,
        )

        salary.full_clean()

    def test_month_zero_is_invalid(self):
        salary = EmployeeSalary(
            employee=self.employee,
            year=1405,
            month=0,
            monthly_wage=30000000,
        )

        with self.assertRaises(ValidationError):
            salary.full_clean()

    def test_month_thirteen_is_invalid(self):
        salary = EmployeeSalary(
            employee=self.employee,
            year=1405,
            month=13,
            monthly_wage=30000000,
        )

        with self.assertRaises(ValidationError):
            salary.full_clean()

    def test_negative_monthly_wage_is_invalid(self):
        salary = EmployeeSalary(
            employee=self.employee,
            year=1405,
            month=6,
            monthly_wage=-1,
        )

        with self.assertRaises(ValidationError):
            salary.full_clean()

    def test_negative_food_allowance_is_invalid(self):
        salary = EmployeeSalary(
            employee=self.employee,
            year=1405,
            month=6,
            monthly_wage=30000000,
            worker_food_allowance=-1,
        )

        with self.assertRaises(ValidationError):
            salary.full_clean()

    def test_negative_housing_allowance_is_invalid(self):
        salary = EmployeeSalary(
            employee=self.employee,
            year=1405,
            month=6,
            monthly_wage=30000000,
            housing_allowance=-1,
        )

        with self.assertRaises(ValidationError):
            salary.full_clean()

    def test_negative_child_allowance_is_invalid(self):
        salary = EmployeeSalary(
            employee=self.employee,
            year=1405,
            month=6,
            monthly_wage=30000000,
            child_allowance=-1,
        )

        with self.assertRaises(ValidationError):
            salary.full_clean()

    def test_negative_marriage_allowance_is_invalid(self):
        salary = EmployeeSalary(
            employee=self.employee,
            year=1405,
            month=6,
            monthly_wage=30000000,
            marriage_allowance=-1,
        )

        with self.assertRaises(ValidationError):
            salary.full_clean()


class PayrollDeductionAPITest(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="payroll_deduction_test",
            password="StrongPassword123",
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.employee = Employee.objects.create(
            personnel_code="DED-001",
            first_name="رضا",
            last_name="کسورات",
            gender="male",
            employee_group="administrative",
            marital_status="married",
            national_id="0076543210",
            birth_date=date(1995, 1, 1),
            start_date=date(2020, 1, 1),
            insurance_date=date(2020, 2, 1),
        )

        self.salary = EmployeeSalary.objects.create(
            employee=self.employee,
            year=1405,
            month=5,
            monthly_wage=30000000,
            worker_food_allowance=5000000,
            housing_allowance=5000000,
            marriage_allowance=2000000,
        )

    def create_deduction(
        self,
        deduction_type="insurance",
        amount=3000000,
        description="تست کسورات",
    ):
        return PayrollDeduction.objects.create(
            salary=self.salary,
            deduction_type=deduction_type,
            amount=amount,
            description=description,
        )

    def test_create_deduction(self):
        response = self.client.post(
            "/api/payroll/deductions/",
            {
                "salary": self.salary.id,
                "deduction_type": "insurance",
                "amount": "3000000",
                "description": "کسور بیمه",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertEqual(
            PayrollDeduction.objects.count(),
            1,
        )

        deduction = PayrollDeduction.objects.get()

        self.assertEqual(
            deduction.salary_id,
            self.salary.id,
        )

        self.assertEqual(
            deduction.deduction_type,
            "insurance",
        )

        self.assertEqual(
            deduction.amount,
            Decimal("3000000"),
        )

    def test_list_deductions(self):
        self.create_deduction()

        response = self.client.get(
            "/api/payroll/deductions/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_retrieve_deduction(self):
        deduction = self.create_deduction()

        response = self.client.get(
            f"/api/payroll/deductions/{deduction.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            deduction.id,
        )

        self.assertEqual(
            response.data["deduction_type"],
            "insurance",
        )

        self.assertEqual(
            response.data["deduction_type_display"],
            deduction.get_deduction_type_display(),
        )

    def test_update_deduction(self):
        deduction = self.create_deduction()

        response = self.client.patch(
            f"/api/payroll/deductions/{deduction.id}/",
            {
                "amount": "4500000",
                "description": "مبلغ اصلاح شد",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        deduction.refresh_from_db()

        self.assertEqual(
            deduction.amount,
            Decimal("4500000"),
        )

        self.assertEqual(
            deduction.description,
            "مبلغ اصلاح شد",
        )

    def test_delete_deduction(self):
        deduction = self.create_deduction()

        response = self.client.delete(
            f"/api/payroll/deductions/{deduction.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            PayrollDeduction.objects.filter(
                id=deduction.id
            ).exists()
        )

    def test_all_deduction_types_are_accepted(self):
        deduction_types = [
            "insurance",
            "tax",
            "advance",
            "loan",
            "absence",
            "other",
        ]

        for index, deduction_type in enumerate(
            deduction_types,
            start=1,
        ):
            deduction = PayrollDeduction.objects.create(
                salary=self.salary,
                deduction_type=deduction_type,
                amount=Decimal(index * 100000),
                description=f"تست {deduction_type}",
            )

            self.assertEqual(
                deduction.deduction_type,
                deduction_type,
            )

        self.assertEqual(
            PayrollDeduction.objects.count(),
            len(deduction_types),
        )

    def test_zero_amount_deduction_is_allowed(self):
        response = self.client.post(
            "/api/payroll/deductions/",
            {
                "salary": self.salary.id,
                "deduction_type": "other",
                "amount": "0",
                "description": "کسور صفر",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        deduction = PayrollDeduction.objects.get()

        self.assertEqual(
            deduction.amount,
            Decimal("0"),
        )

    def test_negative_deduction_amount_is_rejected(self):
        response = self.client.post(
            "/api/payroll/deductions/",
            {
                "salary": self.salary.id,
                "deduction_type": "insurance",
                "amount": "-100000",
                "description": "مبلغ منفی",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

        self.assertEqual(
            PayrollDeduction.objects.count(),
            0,
        )

    def test_invalid_deduction_type_is_rejected(self):
        response = self.client.post(
            "/api/payroll/deductions/",
            {
                "salary": self.salary.id,
                "deduction_type": "invalid_type",
                "amount": "1000000",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

    def test_deduction_belongs_to_salary(self):
        deduction = self.create_deduction(
            deduction_type="tax",
            amount=2500000,
        )

        self.assertEqual(
            deduction.salary,
            self.salary,
        )

        self.assertIn(
            deduction,
            self.salary.deductions.all(),
        )

    def test_multiple_deductions_for_same_salary_are_allowed(self):
        first = self.create_deduction(
            deduction_type="insurance",
            amount=3000000,
        )

        second = self.create_deduction(
            deduction_type="tax",
            amount=1500000,
        )

        third = self.create_deduction(
            deduction_type="loan",
            amount=2000000,
        )

        self.assertEqual(
            self.salary.deductions.count(),
            3,
        )

        self.assertIn(
            first,
            self.salary.deductions.all(),
        )

        self.assertIn(
            second,
            self.salary.deductions.all(),
        )

        self.assertIn(
            third,
            self.salary.deductions.all(),
        )

    def test_delete_salary_cascades_deductions(self):
        deduction = self.create_deduction()

        deduction_id = deduction.id
        salary_id = self.salary.id

        self.salary.delete()

        self.assertFalse(
            EmployeeSalary.objects.filter(
                id=salary_id
            ).exists()
        )

        self.assertFalse(
            PayrollDeduction.objects.filter(
                id=deduction_id
            ).exists()
        )


class PayrollDeductionValidationTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="DED-VAL-001",
            first_name="رضا",
            last_name="تست",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0087654321",
        )

        self.salary = EmployeeSalary.objects.create(
            employee=self.employee,
            year=1405,
            month=6,
            monthly_wage=30000000,
        )

    def test_valid_deduction_data(self):
        deduction = PayrollDeduction(
            salary=self.salary,
            deduction_type="insurance",
            amount=3000000,
            description="تست اعتبارسنجی",
        )

        deduction.full_clean()

    def test_negative_amount_is_invalid(self):
        deduction = PayrollDeduction(
            salary=self.salary,
            deduction_type="insurance",
            amount=-1,
        )

        with self.assertRaises(ValidationError):
            deduction.full_clean()

    def test_zero_amount_is_valid(self):
        deduction = PayrollDeduction(
            salary=self.salary,
            deduction_type="insurance",
            amount=0,
        )

        deduction.full_clean()

    def test_invalid_deduction_type_is_invalid(self):
        deduction = PayrollDeduction(
            salary=self.salary,
            deduction_type="invalid_type",
            amount=1000000,
        )

        with self.assertRaises(ValidationError):
            deduction.full_clean()
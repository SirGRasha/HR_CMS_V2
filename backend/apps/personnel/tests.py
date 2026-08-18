from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from .models import (
    Employee,
    EmployeeBankAccount,
    EmployeeChild,
    EmployeeDocument,
    EmployeePhone,
    EmployeePromissoryNote,
)
from .serializers import (
    EmployeeBankAccountSerializer,
    EmployeeChildSerializer,
    EmployeeDocumentSerializer,
    EmployeePhoneSerializer,
    EmployeePromissoryNoteSerializer,
    EmployeeSerializer,
    validate_iranian_national_id,
)
from apps.accounts.models import User
from apps.organization.models import OrganizationUnit, Position
from apps.personnel.models import Employee


class NationalIDValidationTest(TestCase):

    def test_invalid_length(self):
        with self.assertRaises(ValidationError):
            validate_iranian_national_id("123456789")

    def test_invalid_characters(self):
        with self.assertRaises(ValidationError):
            validate_iranian_national_id("12345678AB")

    def test_all_same_digits(self):
        with self.assertRaises(ValidationError):
            validate_iranian_national_id("1111111111")


class EmployeeSerializerTest(TestCase):

    def test_invalid_national_id(self):
        data = {
            "personnel_code": "TEST-001",
            "first_name": "تست",
            "last_name": "کاربر",
            "national_id": "0012345678",
        }

        serializer = EmployeeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("national_id", serializer.errors)

class EmployeeAPITest(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            password="StrongPassword123",
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.organization_unit = OrganizationUnit.objects.create(
            code="TEST-UNIT-001",
            name="واحد تست",
            unit_type=OrganizationUnit.UnitType.UNIT,
        )

        self.second_organization_unit = OrganizationUnit.objects.create(
            code="TEST-UNIT-002",
            name="واحد تست دوم",
            unit_type=OrganizationUnit.UnitType.UNIT,
        )

        self.position = Position.objects.create(
            code="TEST-POS-001",
            title="سمت تست",
            organization_unit=self.organization_unit,
        )

        self.second_position = Position.objects.create(
            code="TEST-POS-002",
            title="سمت تست دوم",
            organization_unit=self.second_organization_unit,
        )

        self.employee = Employee.objects.create(
            personnel_code="EMP-API-001",
            first_name="تست",
            last_name="کارمند",
            gender="male",
            employee_group="administrative",
            department="فناوری اطلاعات",
            job_title="کارشناس IT",
            national_id="0012345679",
            marital_status="single",
            position=self.position,
        )

        self.second_employee = Employee.objects.create(
            personnel_code="EMP-API-002",
            first_name="کارمند",
            last_name="دوم",
            gender="male",
            employee_group="operational",
            department="مالی",
            job_title="کارشناس مالی",
            national_id="0023456788",
            marital_status="married",
            position=self.second_position,
        )

        self.url = "/api/personnel/employees/"

    def test_list_employees(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        data = response.data
        if isinstance(data, dict) and "results" in data:
            data = data["results"]

        self.assertEqual(len(data), 2)

    def test_retrieve_employee(self):
        response = self.client.get(
            f"{self.url}{self.employee.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["id"],
            self.employee.id,
        )
        self.assertEqual(
            response.data["personnel_code"],
            "EMP-API-001",
        )

    def test_create_employee(self):
        data = {
            "personnel_code": "EMP-API-003",
            "first_name": "کارمند جدید",
            "last_name": "تست",
            "gender": "male",
            "employee_group": "administrative",
            "department": "منابع انسانی",
            "job_title": "کارشناس منابع انسانی",
            "national_id": "0034567895",
            "marital_status": "single",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
            response.data,
        )

        self.assertEqual(
            response.data["personnel_code"],
            "EMP-API-003",
        )

    def test_update_employee(self):
        data = {
            "personnel_code": "EMP-API-001",
            "first_name": "نام جدید",
            "last_name": "نام خانوادگی جدید",
            "gender": "male",
            "employee_group": "administrative",
            "department": "فناوری اطلاعات",
            "job_title": "مدیر IT",
            "national_id": "0012345679",
            "marital_status": "single",
        }

        response = self.client.put(
            f"{self.url}{self.employee.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.employee.refresh_from_db()

        self.assertEqual(
            self.employee.first_name,
            "نام جدید",
        )
        self.assertEqual(
            self.employee.job_title,
            "مدیر IT",
        )

    def test_partial_update_employee(self):
        response = self.client.patch(
            f"{self.url}{self.employee.id}/",
            {
                "job_title": "کارشناس ارشد IT",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.employee.refresh_from_db()

        self.assertEqual(
            self.employee.job_title,
            "کارشناس ارشد IT",
        )

    def test_delete_employee(self):
        employee_id = self.employee.id

        response = self.client.delete(
            f"{self.url}{employee_id}/"
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            Employee.objects.filter(
                id=employee_id
            ).exists()
        )

    def test_filter_by_employee_group(self):
        response = self.client.get(
            self.url,
            {
                "employee_group": "administrative",
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.data
        if isinstance(data, dict) and "results" in data:
            data = data["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["personnel_code"],
            "EMP-API-001",
        )

    def test_filter_by_is_active(self):
        self.second_employee.is_active = False
        self.second_employee.save()

        response = self.client.get(
            self.url,
            {
                "is_active": "true",
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.data
        if isinstance(data, dict) and "results" in data:
            data = data["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["personnel_code"],
            "EMP-API-001",
        )

    def test_filter_by_position(self):
        response = self.client.get(
            self.url,
            {
                "position": self.position.id,
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.data
        if isinstance(data, dict) and "results" in data:
            data = data["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["id"],
            self.employee.id,
        )

    def test_filter_by_organization_unit(self):
        response = self.client.get(
            self.url,
            {
                "organization_unit": self.organization_unit.id,
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.data
        if isinstance(data, dict) and "results" in data:
            data = data["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["id"],
            self.employee.id,
        )

    def test_combined_filters(self):
        response = self.client.get(
            self.url,
            {
                "employee_group": "administrative",
                "is_active": "true",
            },
        )

        self.assertEqual(response.status_code, 200)

        data = response.data
        if isinstance(data, dict) and "results" in data:
            data = data["results"]

        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["personnel_code"],
            "EMP-API-001",
        )

    def test_duplicate_personnel_code_returns_400(self):
        data = {
            "personnel_code": self.employee.personnel_code,
            "first_name": "کارمند",
            "last_name": "تکراری",
            "gender": "male",
            "employee_group": "administrative",
            "department": "فناوری اطلاعات",
            "job_title": "کارشناس",
            "national_id": "0045678905",
            "marital_status": "single",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_national_id_returns_400(self):
        data = {
            "personnel_code": "EMP-API-004",
            "first_name": "کارمند",
            "last_name": "ملی",
            "gender": "male",
            "employee_group": "administrative",
            "department": "فناوری اطلاعات",
            "job_title": "کارشناس",
            "national_id": "123",
            "marital_status": "single",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn(
            "national_id",
            response.data,
        )

    def test_employee_detail_contains_expected_fields(self):
        response = self.client.get(
            f"{self.url}{self.employee.id}/"
        )

        self.assertEqual(response.status_code, 200)

        expected_fields = [
            "id",
            "personnel_code",
            "first_name",
            "last_name",
            "gender",
            "employee_group",
            "national_id",
            "marital_status",
        ]

        for field in expected_fields:
            self.assertIn(
                field,
                response.data,
            )

class EmployeeChildTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="EMP-CHILD-001",
            first_name="تست",
            last_name="آزمایشی",
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
            child_count=1,
            landline_phone="02112345678",
            residence_area="تهران",
            address="آدرس تست",
            transportation_status="personal",
            transportation_description="",
            contract_title="قرارداد تست",
            contract_position="کارشناس IT",
            notes="تست",
            is_active=True,
        )

    def test_create_child(self):
        child = EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند تست",
            birth_date=date(2015, 5, 10),
            education_certificate=False,
            is_active=True,
        )

        self.assertEqual(child.employee, self.employee)
        self.assertEqual(child.name, "فرزند تست")
        self.assertEqual(child.birth_date, date(2015, 5, 10))
        self.assertFalse(child.education_certificate)
        self.assertTrue(child.is_active)

    def test_child_serializer(self):
        data = {
            "employee": self.employee.id,
            "name": "فرزند تست",
            "birth_date": "2015-05-10",
            "education_certificate": False,
            "is_active": True,
        }

        serializer = EmployeeChildSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

        child = serializer.save()

        self.assertEqual(child.employee, self.employee)
        self.assertEqual(child.name, "فرزند تست")

    def test_child_with_education_certificate(self):
        child = EmployeeChild.objects.create(
            employee=self.employee,
            name="فرزند دانش آموز",
            birth_date=date(2005, 9, 15),
            education_certificate=True,
            is_active=True,
        )

        self.assertTrue(child.education_certificate)

    def test_multiple_children(self):
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
            birth_date=date(2018, 2, 2),
            education_certificate=False,
            is_active=True,
        )

        children = EmployeeChild.objects.filter(
            employee=self.employee
        )

        self.assertEqual(children.count(), 2)

class EmployeeDocumentExpiryTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="DOC-TEST-001",
            first_name="تست",
            last_name="مدرک",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0012345679",
        )

    def test_document_without_expiry_date(self):
        document = EmployeeDocument.objects.create(
            employee=self.employee,
            document_type="other",
            title="سند بدون انقضا",
            file="personnel/documents/test.pdf",
            expiry_date=None,
        )

        self.assertIsNone(document.expiry_date)

    def test_document_with_future_expiry_date(self):
        future_date = timezone.localdate() + timedelta(days=30)

        document = EmployeeDocument.objects.create(
            employee=self.employee,
            document_type="other",
            title="سند معتبر",
            file="personnel/documents/test.pdf",
            expiry_date=future_date,
        )

        self.assertGreaterEqual(
            document.expiry_date,
            timezone.localdate(),
        )

    def test_document_with_past_expiry_date(self):
        past_date = timezone.localdate() - timedelta(days=30)

        document = EmployeeDocument.objects.create(
            employee=self.employee,
            document_type="other",
            title="سند منقضی",
            file="personnel/documents/test.pdf",
            expiry_date=past_date,
        )

        self.assertLess(
            document.expiry_date,
            timezone.localdate(),
        )

    def test_document_expiry_status_valid(self):
        document = EmployeeDocument.objects.create(
            employee=self.employee,
            document_type="other",
            title="سند معتبر",
            file="personnel/documents/test.pdf",
            expiry_date=timezone.localdate() + timedelta(days=30),
        )

        serializer = EmployeeDocumentSerializer(document)

        self.assertEqual(
            serializer.data["expiry_status"],
            "valid",
        )

    def test_document_expiry_status_expired(self):
        document = EmployeeDocument.objects.create(
            employee=self.employee,
            document_type="other",
            title="سند منقضی",
            file="personnel/documents/test.pdf",
            expiry_date=timezone.localdate() - timedelta(days=30),
        )

        serializer = EmployeeDocumentSerializer(document)

        self.assertEqual(
            serializer.data["expiry_status"],
            "expired",
        )

    def test_document_expiry_status_no_expiry(self):
        document = EmployeeDocument.objects.create(
            employee=self.employee,
            document_type="other",
            title="سند بدون انقضا",
            file="personnel/documents/test.pdf",
            expiry_date=None,
        )

        serializer = EmployeeDocumentSerializer(document)

        self.assertEqual(
            serializer.data["expiry_status"],
            "no_expiry",
        )

class EmployeeDateValidationTest(TestCase):

    def setUp(self):
        self.valid_data = {
            "personnel_code": "DATE-TEST-001",
            "first_name": "تست",
            "last_name": "تاریخ",
            "gender": "male",
            "employee_group": "administrative",
            "marital_status": "single",
            "national_id": "0012345679",
            "birth_date": "1995-01-01",
            "start_date": "2020-01-01",
            "insurance_date": "2020-02-01",
        }

    def test_birth_date_cannot_be_in_future(self):
        data = self.valid_data.copy()
        data["birth_date"] = "2030-01-01"

        serializer = EmployeeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("birth_date", serializer.errors)

    def test_start_date_cannot_be_in_future(self):
        data = self.valid_data.copy()
        data["start_date"] = "2030-01-01"

        serializer = EmployeeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("start_date", serializer.errors)

    def test_start_date_cannot_be_before_birth_date(self):
        data = self.valid_data.copy()
        data["birth_date"] = "1995-01-01"
        data["start_date"] = "1990-01-01"

        serializer = EmployeeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("start_date", serializer.errors)

    def test_insurance_date_cannot_be_before_start_date(self):
        data = self.valid_data.copy()
        data["start_date"] = "2020-01-01"
        data["insurance_date"] = "2019-01-01"

        serializer = EmployeeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("insurance_date", serializer.errors)

    def test_valid_employee_dates(self):
        serializer = EmployeeSerializer(data=self.valid_data)

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

class EmployeePhonePrimaryTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="PHONE-TEST-001",
            first_name="تست",
            last_name="تلفن",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0012345679",
        )

    def test_only_one_primary_phone_per_employee(self):
        first_phone = EmployeePhone.objects.create(
            employee=self.employee,
            phone_type="mobile",
            phone_number="09121234567",
            is_primary=True,
        )

        second_phone = EmployeePhone.objects.create(
            employee=self.employee,
            phone_type="mobile",
            phone_number="09351234567",
            is_primary=True,
        )

        first_phone.refresh_from_db()
        second_phone.refresh_from_db()

        self.assertFalse(first_phone.is_primary)
        self.assertTrue(second_phone.is_primary)

class EmployeePhoneValidationTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="PHONE-VALID-001",
            first_name="تست",
            last_name="موبایل",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0012345679",
        )

        self.valid_data = {
            "employee": self.employee.id,
            "phone_type": "mobile",
            "phone_number": "09121234567",
            "is_primary": False,
        }

    def test_valid_mobile_number(self):
        serializer = EmployeePhoneSerializer(
            data=self.valid_data
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_mobile_number_must_be_11_digits(self):
        data = self.valid_data.copy()
        data["phone_number"] = "0912123456"

        serializer = EmployeePhoneSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)

    def test_mobile_number_cannot_have_letters(self):
        data = self.valid_data.copy()
        data["phone_number"] = "0912ABC4567"

        serializer = EmployeePhoneSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)

    def test_mobile_number_must_start_with_09(self):
        data = self.valid_data.copy()
        data["phone_number"] = "01121234567"

        serializer = EmployeePhoneSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)

    def test_mobile_number_cannot_be_12_digits(self):
        data = self.valid_data.copy()
        data["phone_number"] = "091212345678"

        serializer = EmployeePhoneSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("phone_number", serializer.errors)

class EmployeeBankAccountValidationTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="BANK-TEST-001",
            first_name="تست",
            last_name="بانک",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0012345679",
            birth_date=date(1995, 1, 1),
            start_date=date(2020, 1, 1),
            insurance_date=date(2020, 2, 1),
        )

        self.valid_data = {
            "employee": self.employee.id,
            "account_number": "1234567890",
            "card_number": "6037991234567890",
            "iban": "IR123456789012345678901234",
            "bank_name": "بانک تست",
            "is_primary": True,
        }

    def test_valid_bank_account(self):
        serializer = EmployeeBankAccountSerializer(
            data=self.valid_data
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_card_number_must_be_16_digits(self):
        data = self.valid_data.copy()
        data["card_number"] = "603799123456789"

        serializer = EmployeeBankAccountSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("card_number", serializer.errors)

    def test_card_number_cannot_have_letters(self):
        data = self.valid_data.copy()
        data["card_number"] = "60379912AB345678"

        serializer = EmployeeBankAccountSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("card_number", serializer.errors)

    def test_iban_must_start_with_ir(self):
        data = self.valid_data.copy()
        data["iban"] = "XX123456789012345678901234"

        serializer = EmployeeBankAccountSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("iban", serializer.errors)

    def test_iban_must_have_26_characters(self):
        data = self.valid_data.copy()
        data["iban"] = "IR12345678901234567890"

        serializer = EmployeeBankAccountSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("iban", serializer.errors)

class EmployeeBankAccountTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="BANK-API-TEST-001",
            first_name="تست",
            last_name="حساب",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0012345679",
            birth_date=date(1995, 1, 1),
            start_date=date(2020, 1, 1),
            insurance_date=date(2020, 2, 1),
        )

        self.other_employee = Employee.objects.create(
            personnel_code="BANK-API-TEST-002",
            first_name="تست",
            last_name="دوم",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0012345687",
            birth_date=date(1996, 1, 1),
            start_date=date(2021, 1, 1),
            insurance_date=date(2021, 2, 1),
        )

    def test_employee_can_have_multiple_bank_accounts(self):
        EmployeeBankAccount.objects.create(
            employee=self.employee,
            account_number="1111111111",
            card_number="6037991111111111",
            iban="IR111111111111111111111111",
            bank_name="بانک اول",
            is_primary=False,
        )

        EmployeeBankAccount.objects.create(
            employee=self.employee,
            account_number="2222222222",
            card_number="6037992222222222",
            iban="IR222222222222222222222222",
            bank_name="بانک دوم",
            is_primary=False,
        )

        self.assertEqual(
            EmployeeBankAccount.objects.filter(
                employee=self.employee
            ).count(),
            2,
        )

    def test_employee_can_have_one_primary_account(self):
        EmployeeBankAccount.objects.create(
            employee=self.employee,
            account_number="1111111111",
            card_number="6037991111111111",
            iban="IR111111111111111111111111",
            bank_name="بانک اول",
            is_primary=True,
        )

        account = EmployeeBankAccount.objects.filter(
            employee=self.employee,
            is_primary=True,
        ).first()

        self.assertIsNotNone(account)

    def test_duplicate_primary_account_is_rejected_by_serializer(self):
        EmployeeBankAccount.objects.create(
            employee=self.employee,
            account_number="1111111111",
            card_number="6037991111111111",
            iban="IR111111111111111111111111",
            bank_name="بانک اول",
            is_primary=True,
        )

        data = {
            "employee": self.employee.id,
            "account_number": "2222222222",
            "card_number": "6037992222222222",
            "iban": "IR222222222222222222222222",
            "bank_name": "بانک دوم",
            "is_primary": True,
        }

        serializer = EmployeeBankAccountSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("is_primary", serializer.errors)

    def test_same_primary_account_can_be_updated(self):
        account = EmployeeBankAccount.objects.create(
            employee=self.employee,
            account_number="1111111111",
            card_number="6037991111111111",
            iban="IR111111111111111111111111",
            bank_name="بانک اول",
            is_primary=True,
        )

        data = {
            "employee": self.employee.id,
            "account_number": "9999999999",
            "card_number": "6037999999999999",
            "iban": "IR999999999999999999999999",
            "bank_name": "بانک به‌روزشده",
            "is_primary": True,
        }

        serializer = EmployeeBankAccountSerializer(
            instance=account,
            data=data,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_primary_account_is_allowed_for_different_employee(self):
        EmployeeBankAccount.objects.create(
            employee=self.employee,
            account_number="1111111111",
            card_number="6037991111111111",
            iban="IR111111111111111111111111",
            bank_name="بانک اول",
            is_primary=True,
        )

        account = EmployeeBankAccount.objects.create(
            employee=self.other_employee,
            account_number="2222222222",
            card_number="6037992222222222",
            iban="IR222222222222222222222222",
            bank_name="بانک دوم",
            is_primary=True,
        )

        self.assertTrue(account.is_primary)
        self.assertEqual(
            account.employee,
            self.other_employee,
        )

    def test_non_primary_account_can_be_created_when_primary_exists(self):
        EmployeeBankAccount.objects.create(
            employee=self.employee,
            account_number="1111111111",
            card_number="6037991111111111",
            iban="IR111111111111111111111111",
            bank_name="بانک اصلی",
            is_primary=True,
        )

        data = {
            "employee": self.employee.id,
            "account_number": "2222222222",
            "card_number": "6037992222222222",
            "iban": "IR222222222222222222222222",
            "bank_name": "بانک دوم",
            "is_primary": False,
        }

        serializer = EmployeeBankAccountSerializer(data=data)

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

class EmployeePromissoryNoteTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="NOTE-TEST-001",
            first_name="تست",
            last_name="سفته",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0012345679",
            birth_date=date(1995, 1, 1),
            start_date=date(2020, 1, 1),
            insurance_date=date(2020, 2, 1),
        )

    def test_create_promissory_note(self):
        note = EmployeePromissoryNote.objects.create(
            employee=self.employee,
            note_number="NOTE-123456",
        )

        self.assertEqual(note.employee, self.employee)
        self.assertEqual(note.note_number, "NOTE-123456")

    def test_promissory_note_serializer(self):
        data = {
            "employee": self.employee.id,
            "note_number": "NOTE-123456",
        }

        serializer = EmployeePromissoryNoteSerializer(data=data)

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_multiple_promissory_notes_for_employee(self):
        EmployeePromissoryNote.objects.create(
            employee=self.employee,
            note_number="NOTE-001",
        )

        EmployeePromissoryNote.objects.create(
            employee=self.employee,
            note_number="NOTE-002",
        )

        notes = EmployeePromissoryNote.objects.filter(
            employee=self.employee
        )

        self.assertEqual(notes.count(), 2)

class EmployeeBankAccountAPITest(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="BANK-API-001",
            first_name="تست",
            last_name="بانک",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0012345679",
            birth_date=date(1995, 1, 1),
            start_date=date(2020, 1, 1),
            insurance_date=date(2020, 2, 1),
        )

    def get_valid_data(self, is_primary=False):
        return {
            "employee": self.employee.id,
            "account_number": "1234567890",
            "card_number": "6037991234567890",
            "iban": "IR123456789012345678901234",
            "bank_name": "بانک تست",
            "is_primary": is_primary,
        }

    def test_list_bank_accounts(self):
        response = self.client.get(
            "/api/personnel/bank-accounts/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_filter_bank_accounts_by_employee(self):
        EmployeeBankAccount.objects.create(
            employee=self.employee,
            account_number="1234567890",
            card_number="6037991234567890",
            iban="IR123456789012345678901234",
            bank_name="بانک تست",
            is_primary=False,
        )

        response = self.client.get(
            f"/api/personnel/bank-accounts/?employee={self.employee.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_create_bank_account(self):
        response = self.client.post(
            "/api/personnel/bank-accounts/",
            self.get_valid_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            EmployeeBankAccount.objects.count(),
            1,
        )

    def test_create_primary_bank_account(self):
        response = self.client.post(
            "/api/personnel/bank-accounts/",
            self.get_valid_data(is_primary=True),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        account = EmployeeBankAccount.objects.get(
            id=response.data["id"]
        )

        self.assertTrue(account.is_primary)

    def test_duplicate_primary_bank_account_returns_400(self):
        EmployeeBankAccount.objects.create(
            employee=self.employee,
            account_number="1111111111",
            card_number="6037991111111111",
            iban="IR111111111111111111111111",
            bank_name="بانک اول",
            is_primary=True,
        )

        data = self.get_valid_data(is_primary=True)

        response = self.client.post(
            "/api/personnel/bank-accounts/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "is_primary",
            response.data,
        )

    def test_create_second_non_primary_account(self):
        EmployeeBankAccount.objects.create(
            employee=self.employee,
            account_number="1111111111",
            card_number="6037991111111111",
            iban="IR111111111111111111111111",
            bank_name="بانک اول",
            is_primary=True,
        )

        data = self.get_valid_data(is_primary=False)

        response = self.client.post(
            "/api/personnel/bank-accounts/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            EmployeeBankAccount.objects.filter(
                employee=self.employee
            ).count(),
            2,
        )

    def test_update_bank_account(self):
        account = EmployeeBankAccount.objects.create(
            employee=self.employee,
            account_number="1111111111",
            card_number="6037991111111111",
            iban="IR111111111111111111111111",
            bank_name="بانک اول",
            is_primary=False,
        )

        response = self.client.patch(
            f"/api/personnel/bank-accounts/{account.id}/",
            {
                "bank_name": "بانک به‌روزشده",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        account.refresh_from_db()

        self.assertEqual(
            account.bank_name,
            "بانک به‌روزشده",
        )

    def test_delete_bank_account(self):
        account = EmployeeBankAccount.objects.create(
            employee=self.employee,
            account_number="1111111111",
            card_number="6037991111111111",
            iban="IR111111111111111111111111",
            bank_name="بانک تست",
            is_primary=False,
        )

        response = self.client.delete(
            f"/api/personnel/bank-accounts/{account.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            EmployeeBankAccount.objects.filter(
                id=account.id
            ).exists()
        )

class EmployeePromissoryNoteAPITest(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="NOTE-API-001",
            first_name="تست",
            last_name="سفته",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0012345679",
            birth_date=date(1995, 1, 1),
            start_date=date(2020, 1, 1),
            insurance_date=date(2020, 2, 1),
        )

    def get_valid_data(self, note_number="NOTE-API-001"):
        return {
            "employee": self.employee.id,
            "note_number": note_number,
        }

    def test_list_promissory_notes(self):
        response = self.client.get(
            "/api/personnel/promissory-notes/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_filter_promissory_notes_by_employee(self):
        EmployeePromissoryNote.objects.create(
            employee=self.employee,
            note_number="NOTE-FILTER-001",
        )

        response = self.client.get(
            f"/api/personnel/promissory-notes/?employee={self.employee.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_create_promissory_note(self):
        response = self.client.post(
            "/api/personnel/promissory-notes/",
            self.get_valid_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            EmployeePromissoryNote.objects.count(),
            1,
        )

        self.assertEqual(
            response.data["note_number"],
            "NOTE-API-001",
        )

    def test_duplicate_promissory_note_for_same_employee_returns_400(self):
        EmployeePromissoryNote.objects.create(
            employee=self.employee,
            note_number="NOTE-DUPLICATE-001",
        )

        response = self.client.post(
            "/api/personnel/promissory-notes/",
            self.get_valid_data(
                note_number="NOTE-DUPLICATE-001"
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "non_field_errors",
            response.data,
        )

    def test_same_note_number_for_different_employee_is_allowed(self):
        second_employee = Employee.objects.create(
            personnel_code="NOTE-API-002",
            first_name="تست دوم",
            last_name="سفته",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0023456788",
            birth_date=date(1994, 1, 1),
            start_date=date(2020, 1, 1),
            insurance_date=date(2020, 2, 1),
        )

        EmployeePromissoryNote.objects.create(
            employee=self.employee,
            note_number="NOTE-SAME-001",
        )

        response = self.client.post(
            "/api/personnel/promissory-notes/",
            {
                "employee": second_employee.id,
                "note_number": "NOTE-SAME-001",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            EmployeePromissoryNote.objects.filter(
                note_number="NOTE-SAME-001"
            ).count(),
            2,
        )

    def test_update_promissory_note(self):
        note = EmployeePromissoryNote.objects.create(
            employee=self.employee,
            note_number="NOTE-UPDATE-001",
        )

        response = self.client.patch(
            f"/api/personnel/promissory-notes/{note.id}/",
            {
                "note_number": "NOTE-UPDATED-001",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        note.refresh_from_db()

        self.assertEqual(
            note.note_number,
            "NOTE-UPDATED-001",
        )

    def test_delete_promissory_note(self):
        note = EmployeePromissoryNote.objects.create(
            employee=self.employee,
            note_number="NOTE-DELETE-001",
        )

        response = self.client.delete(
            f"/api/personnel/promissory-notes/{note.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            EmployeePromissoryNote.objects.filter(
                id=note.id
            ).exists()
        )

    def test_empty_note_number_returns_400(self):
        response = self.client.post(
            "/api/personnel/promissory-notes/",
            {
                "employee": self.employee.id,
                "note_number": "",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "note_number",
            response.data,
        )

class EmployeeDocumentAPITest(APITestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="DOC-API-001",
            first_name="تست",
            last_name="مدرک",
            gender="male",
            employee_group="administrative",
            marital_status="single",
            national_id="0034567896",
            birth_date=date(1995, 1, 1),
            start_date=date(2020, 1, 1),
            insurance_date=date(2020, 2, 1),
        )

    def create_document(
        self,
        file_name="test.pdf",
        content=b"test document",
        expiry_date=None,
        document_type="national_id",
        is_verified=False,
    ):
        uploaded_file = SimpleUploadedFile(
            file_name,
            content,
            content_type="application/pdf",
        )

        data = {
            "employee": self.employee.id,
            "document_type": document_type,
            "title": "مدرک تست",
            "file": uploaded_file,
            "is_verified": is_verified,
        }

        # در multipart نمی‌توان None ارسال کرد.
        # اگر تاریخ وجود داشته باشد، آن را ارسال می‌کنیم.
        if expiry_date is not None:
            data["expiry_date"] = expiry_date

        return self.client.post(
            "/api/personnel/documents/",
            data,
            format="multipart",
        )

    def test_list_documents(self):
        response = self.client.get(
            "/api/personnel/documents/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_create_pdf_document(self):
        response = self.create_document()

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertEqual(
            EmployeeDocument.objects.count(),
            1,
        )

    def test_filter_documents_by_employee(self):
        self.create_document()

        response = self.client.get(
            f"/api/personnel/documents/?employee={self.employee.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_expired_document_filter(self):
        self.create_document(
            expiry_date="2020-01-01",
        )

        response = self.client.get(
            "/api/personnel/documents/?expiry_status=expired"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_valid_document_filter(self):
        self.create_document(
            expiry_date="2030-01-01",
        )

        response = self.client.get(
            "/api/personnel/documents/?expiry_status=valid"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_no_expiry_document_filter(self):
        self.create_document(
            expiry_date=None,
        )

        response = self.client.get(
            "/api/personnel/documents/?expiry_status=no_expiry"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_verified_document_filter(self):
        self.create_document(
            is_verified=True,
        )

        response = self.client.get(
            "/api/personnel/documents/?is_verified=true"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_unverified_document_filter(self):
        self.create_document(
            is_verified=False,
        )

        response = self.client.get(
            "/api/personnel/documents/?is_verified=false"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_document_type_filter(self):
        self.create_document(
            document_type="national_id",
        )

        response = self.client.get(
            "/api/personnel/documents/?document_type=national_id"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_invalid_file_extension_is_rejected(self):
        response = self.create_document(
            file_name="malware.exe",
            content=b"fake executable",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "file",
            response.data,
        )

        self.assertEqual(
            EmployeeDocument.objects.count(),
            0,
        )

    def test_file_larger_than_10mb_is_rejected(self):
        large_content = b"x" * (
            10 * 1024 * 1024 + 1
        )

        response = self.create_document(
            file_name="large.pdf",
            content=large_content,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "file",
            response.data,
        )

        self.assertEqual(
            EmployeeDocument.objects.count(),
            0,
        )
    def test_retrieve_document(self):
        response = self.create_document(
            expiry_date="2030-01-01",
            is_verified=True,
            document_type="national_id",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        document_id = response.data["id"]

        response = self.client.get(
            f"/api/personnel/documents/{document_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            document_id,
        )

        self.assertEqual(
            response.data["document_type"],
            "national_id",
        )

        self.assertTrue(
            response.data["is_verified"],
        )

    def test_update_document(self):
        response = self.create_document(
            expiry_date="2030-01-01",
            is_verified=False,
            document_type="national_id",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        document_id = response.data["id"]

        response = self.client.patch(
            f"/api/personnel/documents/{document_id}/",
            {
                "title": "مدرک ملی به‌روزشده",
                "is_verified": True,
                "expiry_date": "2035-01-01",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        document = EmployeeDocument.objects.get(
            id=document_id
        )

        self.assertEqual(
            document.title,
            "مدرک ملی به‌روزشده",
        )

        self.assertTrue(
            document.is_verified,
        )

        self.assertEqual(
            str(document.expiry_date),
            "2035-01-01",
        )

    def test_delete_document(self):
        response = self.create_document(
            document_type="national_id",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        document_id = response.data["id"]

        response = self.client.delete(
            f"/api/personnel/documents/{document_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            EmployeeDocument.objects.filter(
                id=document_id
            ).exists()
        )

    def test_update_document_type(self):
        response = self.create_document(
            document_type="national_id",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        document_id = response.data["id"]

        response = self.client.patch(
            f"/api/personnel/documents/{document_id}/",
            {
                "document_type": "education",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        document = EmployeeDocument.objects.get(
            id=document_id
        )

        self.assertEqual(
            document.document_type,
            "education",
        )

    def test_update_document_to_invalid_type_is_rejected(self):
        response = self.create_document(
            document_type="national_id",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        document_id = response.data["id"]

        response = self.client.patch(
            f"/api/personnel/documents/{document_id}/",
            {
                "document_type": "identity",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        document = EmployeeDocument.objects.get(
            id=document_id
        )

        self.assertEqual(
            document.document_type,
            "national_id",
        )

class EmployeeUserRelationTest(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            personnel_code="EMP-USER-001",
            first_name="Reza",
            last_name="Test",
            gender="male",
            employee_group="administrative",
            national_id="0012345678",
            marital_status="single",
        )

        self.user = User.objects.create_user(
            username="employee_user",
            password="StrongPassword123",
            first_name="Reza",
            last_name="Test",
        )

    def test_employee_can_exist_without_user(self):
        self.assertIsNone(
            self.employee.user
        )

    def test_employee_can_be_linked_to_user(self):
        self.employee.user = self.user
        self.employee.save()

        self.employee.refresh_from_db()

        self.assertEqual(
            self.employee.user,
            self.user,
        )

    def test_user_can_access_linked_employee(self):
        self.employee.user = self.user
        self.employee.save()

        self.assertEqual(
            self.user.employee,
            self.employee,
        )

    def test_employee_user_relation_is_one_to_one(self):
        self.employee.user = self.user
        self.employee.save()

        another_employee = Employee.objects.create(
            personnel_code="EMP-USER-002",
            first_name="Another",
            last_name="Employee",
            gender="male",
            employee_group="administrative",
            national_id="0012345686",
            marital_status="single",
        )

        another_employee.user = self.user

        with self.assertRaises(Exception):
            another_employee.save()

    def test_deleting_user_does_not_delete_employee(self):
        self.employee.user = self.user
        self.employee.save()

        self.user.delete()

        self.employee.refresh_from_db()

        self.assertTrue(
            Employee.objects.filter(
                id=self.employee.id
            ).exists()
        )

        self.assertIsNone(
            self.employee.user
        )
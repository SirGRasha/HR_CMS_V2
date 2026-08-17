from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.organization.models import OrganizationUnit, Position
from apps.organization.serializers import (
    OrganizationUnitSerializer,
    PositionSerializer,
)


class OrganizationUnitTest(TestCase):

    def test_create_organization_unit(self):
        unit = OrganizationUnit.objects.create(
            code="IT",
            name="واحد فناوری اطلاعات",
            unit_type=OrganizationUnit.UnitType.UNIT,
        )

        self.assertEqual(unit.code, "IT")
        self.assertEqual(unit.name, "واحد فناوری اطلاعات")
        self.assertEqual(
            unit.unit_type,
            OrganizationUnit.UnitType.UNIT,
        )
        self.assertTrue(unit.is_active)

    def test_organization_unit_code_must_be_unique(self):
        OrganizationUnit.objects.create(
            code="IT",
            name="واحد فناوری اطلاعات",
            unit_type=OrganizationUnit.UnitType.UNIT,
        )

        with self.assertRaises(IntegrityError):
            OrganizationUnit.objects.create(
                code="IT",
                name="واحد فناوری دوم",
                unit_type=OrganizationUnit.UnitType.UNIT,
            )

    def test_organization_unit_can_have_parent(self):
        company = OrganizationUnit.objects.create(
            code="COMP",
            name="شرکت",
            unit_type=OrganizationUnit.UnitType.COMPANY,
        )

        department = OrganizationUnit.objects.create(
            code="IT",
            name="واحد فناوری اطلاعات",
            unit_type=OrganizationUnit.UnitType.UNIT,
            parent=company,
        )

        self.assertEqual(department.parent, company)
        self.assertIn(department, company.children.all())

    def test_root_organization_unit_has_no_parent(self):
        company = OrganizationUnit.objects.create(
            code="COMP",
            name="شرکت",
            unit_type=OrganizationUnit.UnitType.COMPANY,
        )

        self.assertIsNone(company.parent)

    def test_organization_unit_can_be_deactivated(self):
        unit = OrganizationUnit.objects.create(
            code="IT",
            name="واحد فناوری اطلاعات",
            unit_type=OrganizationUnit.UnitType.UNIT,
        )

        unit.is_active = False
        unit.save()

        unit.refresh_from_db()

        self.assertFalse(unit.is_active)

    def test_organization_unit_string_representation(self):
        unit = OrganizationUnit.objects.create(
            code="IT",
            name="واحد فناوری اطلاعات",
            unit_type=OrganizationUnit.UnitType.UNIT,
        )

        self.assertEqual(
            str(unit),
            "IT - واحد فناوری اطلاعات",
        )

    def test_organization_unit_parent_protected_when_children_exist(self):
        parent = OrganizationUnit.objects.create(
            code="COMP",
            name="شرکت",
            unit_type=OrganizationUnit.UnitType.COMPANY,
        )

        OrganizationUnit.objects.create(
            code="IT",
            name="واحد فناوری اطلاعات",
            unit_type=OrganizationUnit.UnitType.UNIT,
            parent=parent,
        )

        with self.assertRaises(ProtectedError):
            parent.delete()


class PositionTest(TestCase):

    def setUp(self):
        self.unit = OrganizationUnit.objects.create(
            code="IT",
            name="واحد فناوری اطلاعات",
            unit_type=OrganizationUnit.UnitType.UNIT,
        )

    def test_create_position(self):
        position = Position.objects.create(
            code="IT-001",
            title="کارشناس IT",
            organization_unit=self.unit,
        )

        self.assertEqual(position.code, "IT-001")
        self.assertEqual(position.title, "کارشناس IT")
        self.assertEqual(position.organization_unit, self.unit)
        self.assertTrue(position.is_active)

    def test_position_code_must_be_unique(self):
        Position.objects.create(
            code="IT-001",
            title="کارشناس IT",
            organization_unit=self.unit,
        )

        with self.assertRaises(IntegrityError):
            Position.objects.create(
                code="IT-001",
                title="کارشناس IT دوم",
                organization_unit=self.unit,
            )

    def test_unit_can_have_multiple_positions(self):
        position_1 = Position.objects.create(
            code="IT-001",
            title="کارشناس IT",
            organization_unit=self.unit,
        )

        position_2 = Position.objects.create(
            code="IT-002",
            title="کارشناس شبکه",
            organization_unit=self.unit,
        )

        self.assertEqual(self.unit.positions.count(), 2)
        self.assertIn(position_1, self.unit.positions.all())
        self.assertIn(position_2, self.unit.positions.all())

    def test_position_can_be_deactivated(self):
        position = Position.objects.create(
            code="IT-001",
            title="کارشناس IT",
            organization_unit=self.unit,
        )

        position.is_active = False
        position.save()

        position.refresh_from_db()

        self.assertFalse(position.is_active)

    def test_position_string_representation(self):
        position = Position.objects.create(
            code="IT-001",
            title="کارشناس IT",
            organization_unit=self.unit,
        )

        self.assertEqual(
            str(position),
            "IT-001 - کارشناس IT",
        )

    def test_position_requires_organization_unit(self):
        with self.assertRaises(IntegrityError):
            Position.objects.create(
                code="IT-001",
                title="کارشناس IT",
                organization_unit=None,
            )

    def test_organization_unit_cannot_be_deleted_if_position_exists(self):
        Position.objects.create(
            code="IT-001",
            title="کارشناس IT",
            organization_unit=self.unit,
        )

        with self.assertRaises(ProtectedError):
            self.unit.delete()


class OrganizationUnitSerializerTest(TestCase):

    def test_valid_serializer(self):
        serializer = OrganizationUnitSerializer(
            data={
                "code": "COMP",
                "name": "شرکت",
                "unit_type": "company",
                "is_active": True,
                "description": "ساختار اصلی شرکت",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_serializer_rejects_invalid_unit_type(self):
        serializer = OrganizationUnitSerializer(
            data={
                "code": "INVALID",
                "name": "واحد نامعتبر",
                "unit_type": "invalid_type",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("unit_type", serializer.errors)

    def test_serializer_read_only_fields(self):
        serializer = OrganizationUnitSerializer()

        self.assertIn("id", serializer.fields)
        self.assertIn("created_at", serializer.fields)
        self.assertIn("updated_at", serializer.fields)


class PositionSerializerTest(TestCase):

    def setUp(self):
        self.unit = OrganizationUnit.objects.create(
            code="IT",
            name="واحد فناوری اطلاعات",
            unit_type=OrganizationUnit.UnitType.UNIT,
        )

    def test_valid_serializer(self):
        serializer = PositionSerializer(
            data={
                "code": "IT-001",
                "title": "کارشناس IT",
                "organization_unit": self.unit.id,
                "is_active": True,
                "description": "سمت کارشناس IT",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_serializer_requires_organization_unit(self):
        serializer = PositionSerializer(
            data={
                "code": "IT-001",
                "title": "کارشناس IT",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "organization_unit",
            serializer.errors,
        )

    def test_serializer_read_only_fields(self):
        serializer = PositionSerializer()

        self.assertIn("id", serializer.fields)
        self.assertIn("created_at", serializer.fields)
        self.assertIn("updated_at", serializer.fields)


class OrganizationUnitAPITest(APITestCase):

    def setUp(self):
        self.unit = OrganizationUnit.objects.create(
            code="IT",
            name="واحد فناوری اطلاعات",
            unit_type=OrganizationUnit.UnitType.UNIT,
            is_active=True,
        )

        self.inactive_unit = OrganizationUnit.objects.create(
            code="HR",
            name="واحد منابع انسانی",
            unit_type=OrganizationUnit.UnitType.DEPARTMENT,
            is_active=False,
        )

    def get_valid_data(self):
        return {
            "code": "FIN",
            "name": "واحد مالی",
            "unit_type": "department",
            "is_active": True,
            "description": "واحد مالی شرکت",
        }

    def test_list_units(self):
        response = self.client.get(
            "/api/organization/units/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 2)

    def test_create_unit(self):
        response = self.client.post(
            "/api/organization/units/",
            self.get_valid_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertEqual(
            OrganizationUnit.objects.count(),
            3,
        )

    def test_retrieve_unit(self):
        response = self.client.get(
            f"/api/organization/units/{self.unit.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.unit.id,
        )

    def test_update_unit(self):
        response = self.client.patch(
            f"/api/organization/units/{self.unit.id}/",
            {
                "name": "واحد فناوری اطلاعات و ارتباطات",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.unit.refresh_from_db()

        self.assertEqual(
            self.unit.name,
            "واحد فناوری اطلاعات و ارتباطات",
        )

    def test_delete_unit(self):
        response = self.client.delete(
            f"/api/organization/units/{self.unit.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            OrganizationUnit.objects.filter(
                id=self.unit.id
            ).exists()
        )

    def test_filter_units_by_active(self):
        response = self.client.get(
            "/api/organization/units/?is_active=true"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["code"],
            "IT",
        )

    def test_filter_units_by_inactive(self):
        response = self.client.get(
            "/api/organization/units/?is_active=false"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["code"],
            "HR",
        )

    def test_filter_units_by_type(self):
        response = self.client.get(
            "/api/organization/units/?unit_type=department"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["code"],
            "HR",
        )

    def test_filter_root_units(self):
        response = self.client.get(
            "/api/organization/units/?parent=null"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 2)

    def test_filter_child_units_by_parent(self):
        child = OrganizationUnit.objects.create(
            code="IT-NET",
            name="واحد شبکه",
            unit_type=OrganizationUnit.UnitType.SECTION,
            parent=self.unit,
        )

        response = self.client.get(
            f"/api/organization/units/?parent={self.unit.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["id"],
            child.id,
        )

    def test_duplicate_unit_code_returns_400(self):
        response = self.client.post(
            "/api/organization/units/",
            {
                **self.get_valid_data(),
                "code": "IT",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "code",
            response.data,
        )


class PositionAPITest(APITestCase):

    def setUp(self):
        self.unit = OrganizationUnit.objects.create(
            code="IT",
            name="واحد فناوری اطلاعات",
            unit_type=OrganizationUnit.UnitType.UNIT,
        )

        self.position = Position.objects.create(
            code="IT-001",
            title="کارشناس IT",
            organization_unit=self.unit,
        )

        self.inactive_position = Position.objects.create(
            code="IT-002",
            title="کارشناس شبکه",
            organization_unit=self.unit,
            is_active=False,
        )

    def get_valid_data(self):
        return {
            "code": "IT-003",
            "title": "مدیر IT",
            "organization_unit": self.unit.id,
            "is_active": True,
            "description": "مدیر واحد فناوری اطلاعات",
        }

    def test_list_positions(self):
        response = self.client.get(
            "/api/organization/positions/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 2)

    def test_create_position(self):
        response = self.client.post(
            "/api/organization/positions/",
            self.get_valid_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertEqual(
            Position.objects.count(),
            3,
        )

    def test_retrieve_position(self):
        response = self.client.get(
            f"/api/organization/positions/{self.position.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.position.id,
        )

    def test_update_position(self):
        response = self.client.patch(
            f"/api/organization/positions/{self.position.id}/",
            {
                "title": "کارشناس ارشد IT",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.position.refresh_from_db()

        self.assertEqual(
            self.position.title,
            "کارشناس ارشد IT",
        )

    def test_delete_position(self):
        response = self.client.delete(
            f"/api/organization/positions/{self.position.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Position.objects.filter(
                id=self.position.id
            ).exists()
        )

    def test_filter_positions_by_active(self):
        response = self.client.get(
            "/api/organization/positions/?is_active=true"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["code"],
            "IT-001",
        )

    def test_filter_positions_by_inactive(self):
        response = self.client.get(
            "/api/organization/positions/?is_active=false"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["code"],
            "IT-002",
        )

    def test_filter_positions_by_organization_unit(self):
        response = self.client.get(
            f"/api/organization/positions/?organization_unit={self.unit.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 2)

    def test_duplicate_position_code_returns_400(self):
        response = self.client.post(
            "/api/organization/positions/",
            {
                **self.get_valid_data(),
                "code": "IT-001",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "code",
            response.data,
        )
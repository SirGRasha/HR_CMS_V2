from rest_framework import status
from rest_framework.test import APITestCase

from apps.organization.models import OrganizationUnit, Position


class OrganizationUnitAPITest(APITestCase):

    def setUp(self):
        self.company = OrganizationUnit.objects.create(
            code="COMP",
            name="شرکت",
            unit_type=OrganizationUnit.UnitType.COMPANY,
        )

        self.it_unit = OrganizationUnit.objects.create(
            code="IT",
            name="واحد فناوری اطلاعات",
            unit_type=OrganizationUnit.UnitType.UNIT,
            parent=self.company,
        )

        self.hr_unit = OrganizationUnit.objects.create(
            code="HR",
            name="واحد منابع انسانی",
            unit_type=OrganizationUnit.UnitType.UNIT,
            parent=self.company,
        )

    def test_list_organization_units(self):
        response = self.client.get(
            "/api/organization/units/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            3,
        )

    def test_create_organization_unit(self):
        response = self.client.post(
            "/api/organization/units/",
            {
                "code": "FIN",
                "name": "واحد مالی",
                "unit_type": "unit",
                "parent": self.company.id,
                "is_active": True,
                "description": "واحد مالی شرکت",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertEqual(
            response.data["code"],
            "FIN",
        )

        self.assertEqual(
            response.data["parent"],
            self.company.id,
        )

        self.assertTrue(
            OrganizationUnit.objects.filter(
                code="FIN"
            ).exists()
        )

    def test_retrieve_organization_unit(self):
        response = self.client.get(
            f"/api/organization/units/{self.it_unit.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.it_unit.id,
        )

        self.assertEqual(
            response.data["code"],
            "IT",
        )

    def test_update_organization_unit(self):
        response = self.client.patch(
            f"/api/organization/units/{self.it_unit.id}/",
            {
                "name": "واحد فناوری اطلاعات و ارتباطات",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        self.it_unit.refresh_from_db()

        self.assertEqual(
            self.it_unit.name,
            "واحد فناوری اطلاعات و ارتباطات",
        )

    def test_delete_organization_unit(self):
        response = self.client.delete(
            f"/api/organization/units/{self.hr_unit.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            OrganizationUnit.objects.filter(
                id=self.hr_unit.id
            ).exists()
        )

    def test_filter_active_units(self):
        self.hr_unit.is_active = False
        self.hr_unit.save()

        response = self.client.get(
            "/api/organization/units/",
            {
                "is_active": "true",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

        self.assertTrue(
            all(
                item["is_active"]
                for item in response.data
            )
        )

    def test_filter_inactive_units(self):
        self.hr_unit.is_active = False
        self.hr_unit.save()

        response = self.client.get(
            "/api/organization/units/",
            {
                "is_active": "false",
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

        self.assertFalse(
            response.data[0]["is_active"]
        )

    def test_filter_units_by_type(self):
        response = self.client.get(
            "/api/organization/units/",
            {
                "unit_type": "unit",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

        self.assertTrue(
            all(
                item["unit_type"] == "unit"
                for item in response.data
            )
        )

    def test_filter_units_by_parent(self):
        response = self.client.get(
            "/api/organization/units/",
            {
                "parent": self.company.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

        self.assertTrue(
            all(
                item["parent"] == self.company.id
                for item in response.data
            )
        )

    def test_filter_root_units(self):
        response = self.client.get(
            "/api/organization/units/",
            {
                "parent": "null",
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

        self.assertIsNone(
            response.data[0]["parent"]
        )

    def test_create_unit_with_invalid_parent_is_rejected(self):
        response = self.client.post(
            "/api/organization/units/",
            {
                "code": "BAD",
                "name": "واحد نامعتبر",
                "unit_type": "unit",
                "parent": 999999,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )


class PositionAPITest(APITestCase):

    def setUp(self):
        self.unit = OrganizationUnit.objects.create(
            code="IT",
            name="واحد فناوری اطلاعات",
            unit_type=OrganizationUnit.UnitType.UNIT,
        )

        self.other_unit = OrganizationUnit.objects.create(
            code="HR",
            name="واحد منابع انسانی",
            unit_type=OrganizationUnit.UnitType.UNIT,
        )

        self.position = Position.objects.create(
            code="IT-001",
            title="کارشناس IT",
            organization_unit=self.unit,
        )

        self.second_position = Position.objects.create(
            code="IT-002",
            title="کارشناس شبکه",
            organization_unit=self.unit,
        )

    def test_list_positions(self):
        response = self.client.get(
            "/api/organization/positions/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    def test_create_position(self):
        response = self.client.post(
            "/api/organization/positions/",
            {
                "code": "HR-001",
                "title": "کارشناس منابع انسانی",
                "organization_unit": self.other_unit.id,
                "is_active": True,
                "description": "سمت منابع انسانی",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertEqual(
            response.data["code"],
            "HR-001",
        )

        self.assertEqual(
            response.data["organization_unit"],
            self.other_unit.id,
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

        self.assertEqual(
            response.data["code"],
            "IT-001",
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
            response.data,
        )

        self.position.refresh_from_db()

        self.assertEqual(
            self.position.title,
            "کارشناس ارشد IT",
        )

    def test_delete_position(self):
        response = self.client.delete(
            f"/api/organization/positions/{self.second_position.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Position.objects.filter(
                id=self.second_position.id
            ).exists()
        )

    def test_filter_active_positions(self):
        self.second_position.is_active = False
        self.second_position.save()

        response = self.client.get(
            "/api/organization/positions/",
            {
                "is_active": "true",
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

        self.assertTrue(
            response.data[0]["is_active"]
        )

    def test_filter_inactive_positions(self):
        self.second_position.is_active = False
        self.second_position.save()

        response = self.client.get(
            "/api/organization/positions/",
            {
                "is_active": "false",
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

        self.assertFalse(
            response.data[0]["is_active"]
        )

    def test_filter_positions_by_organization_unit(self):
        response = self.client.get(
            "/api/organization/positions/",
            {
                "organization_unit": self.unit.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

        self.assertTrue(
            all(
                item["organization_unit"]
                == self.unit.id
                for item in response.data
            )
        )

    def test_create_position_with_invalid_unit_is_rejected(self):
        response = self.client.post(
            "/api/organization/positions/",
            {
                "code": "BAD-001",
                "title": "سمت نامعتبر",
                "organization_unit": 999999,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

    def test_create_position_without_unit_is_rejected(self):
        response = self.client.post(
            "/api/organization/positions/",
            {
                "code": "BAD-002",
                "title": "سمت بدون واحد",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            response.data,
        )

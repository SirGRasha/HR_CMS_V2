from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.personnel.models import Employee

from .models import HRRequest


class HRRequestModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
        )

        self.employee = Employee.objects.create(
            first_name="Reza",
            last_name="Test",
        )

    def test_create_request(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
            description="Request for annual leave.",
        )

        self.assertEqual(
            request.status,
            HRRequest.Status.PENDING,
        )

        self.assertEqual(
            request.requested_by,
            self.user,
        )

        self.assertEqual(
            request.employee,
            self.employee,
        )


class HRRequestAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
        )

        self.staff = User.objects.create_user(
            username="staff",
            password="StrongPassword123",
            is_staff=True,
        )

        self.employee = Employee.objects.create(
            first_name="Reza",
            last_name="Test",
        )

        self.url = "/api/requests/requests/"

    def test_unauthenticated_user_cannot_list_requests(self):
        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_create_request(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {
                "employee": self.employee.id,
                "request_type": "LEAVE",
                "title": "Annual Leave",
                "description": "Five days leave.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        request = HRRequest.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            request.requested_by,
            self.user,
        )

        self.assertEqual(
            request.status,
            HRRequest.Status.PENDING,
        )

    def test_user_only_sees_own_requests(self):
        other_user = User.objects.create_user(
            username="other",
            password="StrongPassword123",
        )

        HRRequest.objects.create(
            employee=self.employee,
            requested_by=other_user,
            request_type="LEAVE",
            title="Other Request",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            0,
        )

    def test_staff_can_list_all_requests(self):
        HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type="LEAVE",
            title="My Request",
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_user_cannot_change_status(self):
        self.client.force_authenticate(
            user=self.user
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type="LEAVE",
            title="Annual Leave",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": "APPROVED",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_staff_can_approve_request(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type="LEAVE",
            title="Annual Leave",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": "APPROVED",
                "response": "Approved.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            HRRequest.Status.APPROVED,
        )

        self.assertEqual(
            request.reviewed_by,
            self.staff,
        )

        self.assertIsNotNone(
            request.reviewed_at
        )

    def test_finalized_request_cannot_be_modified(self):
        self.client.force_authenticate(
            user=self.user
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type="LEAVE",
            title="Annual Leave",
            status=HRRequest.Status.APPROVED,
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "title": "Changed",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_request_creation_creates_audit_log(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {
                "employee": self.employee.id,
                "request_type": "LEAVE",
                "title": "Annual Leave",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        from apps.audit.models import AuditLog

        request_id = response.data["id"]

        audit = AuditLog.objects.get(
            object_id=str(request_id),
            action=AuditLog.Action.CREATE,
        )

        self.assertEqual(
            audit.actor,
            self.user,
        )

        self.assertEqual(
            audit.app_label,
            "requests",
        )

        self.assertEqual(
            audit.model_name,
            "hrrequest",
        )
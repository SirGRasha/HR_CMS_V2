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

    def test_staff_approval_creates_notification(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
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

        from apps.notifications.models import Notification

        notification = Notification.objects.get(
            recipient=self.user,
            related_model="HRRequest",
            related_object_id=str(request.id),
        )

        self.assertEqual(
            notification.notification_type,
            Notification.NotificationType.SUCCESS,
        )

        self.assertEqual(
            notification.title,
            "درخواست شما تأیید شد",
        )

    def test_staff_rejection_creates_notification(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": "REJECTED",
                "response": "Rejected.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        from apps.notifications.models import Notification

        notification = Notification.objects.get(
            recipient=self.user,
            related_model="HRRequest",
            related_object_id=str(request.id),
        )

        self.assertEqual(
            notification.notification_type,
            Notification.NotificationType.ERROR,
        )

        self.assertEqual(
            notification.title,
            "درخواست شما رد شد",
        )

    def test_staff_cannot_delete_approved_request(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Approved Request",
            status=HRRequest.Status.APPROVED,
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.delete(
            f"{self.url}{request.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            HRRequest.objects.filter(
                id=request.id
            ).exists()
        )


    def test_staff_cannot_delete_rejected_request(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Rejected Request",
            status=HRRequest.Status.REJECTED,
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.delete(
            f"{self.url}{request.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            HRRequest.objects.filter(
                id=request.id
            ).exists()
        )


    def test_staff_cannot_delete_cancelled_request(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Cancelled Request",
            status=HRRequest.Status.CANCELLED,
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.delete(
            f"{self.url}{request.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            HRRequest.objects.filter(
                id=request.id
            ).exists()
        )


    def test_staff_can_delete_pending_request(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Pending Request",
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.delete(
            f"{self.url}{request.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            HRRequest.objects.filter(
                id=request.id
            ).exists()
        )


    def test_user_cannot_delete_approved_request(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Approved Request",
            status=HRRequest.Status.APPROVED,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            f"{self.url}{request.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            HRRequest.objects.filter(
                id=request.id
            ).exists()
        )


    def test_user_cannot_delete_rejected_request(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Rejected Request",
            status=HRRequest.Status.REJECTED,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            f"{self.url}{request.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            HRRequest.objects.filter(
                id=request.id
            ).exists()
        )


    def test_user_cannot_delete_cancelled_request(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Cancelled Request",
            status=HRRequest.Status.CANCELLED,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            f"{self.url}{request.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            HRRequest.objects.filter(
                id=request.id
            ).exists()
        )

    def test_staff_can_reject_request(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.REJECTED,
                "response": "Rejected due to staffing requirements.",
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
            HRRequest.Status.REJECTED,
        )

        self.assertEqual(
            request.reviewed_by,
            self.staff,
        )

        self.assertIsNotNone(
            request.reviewed_at
        )


    def test_staff_can_cancel_request(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.CANCELLED,
                "response": "Request cancelled.",
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
            HRRequest.Status.CANCELLED,
        )

        self.assertEqual(
            request.reviewed_by,
            self.staff,
        )

        self.assertIsNotNone(
            request.reviewed_at
        )

    def test_pending_can_transition_to_approved(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.APPROVED,
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

    def test_pending_can_transition_to_rejected(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.REJECTED,
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
            HRRequest.Status.REJECTED,
        )

    def test_pending_can_transition_to_cancelled(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.CANCELLED,
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
            HRRequest.Status.CANCELLED,
        )

    def test_approved_cannot_transition_to_rejected(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
            status=HRRequest.Status.APPROVED,
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.REJECTED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            HRRequest.Status.APPROVED,
        )


    def test_rejected_cannot_transition_to_approved(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
            status=HRRequest.Status.REJECTED,
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.APPROVED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            HRRequest.Status.REJECTED,
        )


    def test_cancelled_cannot_transition_to_approved(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
            status=HRRequest.Status.CANCELLED,
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.APPROVED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            HRRequest.Status.CANCELLED,
        )

    def test_normal_user_cannot_transition_pending_request(self):
        self.client.force_authenticate(
            user=self.user
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.CANCELLED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            HRRequest.Status.PENDING,
        )

    def test_staff_update_without_status_does_not_set_reviewer(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Original Title",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "title": "Updated Title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.title,
            "Updated Title",
        )

        self.assertIsNone(
            request.reviewed_by
        )

        self.assertIsNone(
            request.reviewed_at
        )

    def test_user_cannot_change_employee(self):
        another_employee = Employee.objects.create(
            first_name="Other",
            last_name="Employee",
            personnel_code="EMP-002",
            national_id="1234567890",
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "employee": another_employee.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.employee,
            self.employee,
        )

        self.assertNotEqual(
            request.employee,
            another_employee,
        )

    def test_user_cannot_change_request_type(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "request_type": HRRequest.RequestType.LOAN,
            },
            format="json",
        )

        request.refresh_from_db()

        self.assertEqual(
            request.request_type,
            HRRequest.RequestType.LEAVE,
        )

        self.assertNotEqual(
            request.request_type,
            HRRequest.RequestType.LOAN,
        )


    def test_user_cannot_change_response(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
            response="Original response.",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "response": "Forged response.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.response,
            "Forged response.",
        )


    def test_user_cannot_change_requested_by(self):
        other_user = User.objects.create_user(
            username="other_requester",
            password="StrongPassword123",
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "requested_by": other_user.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.requested_by,
            self.user,
        )


    def test_user_cannot_change_reviewed_by(self):
        other_user = User.objects.create_user(
            username="reviewer",
            password="StrongPassword123",
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "reviewed_by": other_user.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertIsNone(
            request.reviewed_by
        )


    def test_user_cannot_change_reviewed_at(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "reviewed_at": "2026-08-22T10:00:00Z",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertIsNone(
            request.reviewed_at
        )


    def test_user_cannot_forge_requested_by_on_create(self):
        other_user = User.objects.create_user(
            username="forged_user",
            password="StrongPassword123",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {
                "employee": self.employee.id,
                "requested_by": other_user.id,
                "request_type": HRRequest.RequestType.LEAVE,
                "title": "Forged Request",
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


    def test_staff_update_without_status_preserves_reviewer_metadata(self):
        reviewer = User.objects.create_user(
            username="existing_reviewer",
            password="StrongPassword123",
            is_staff=True,
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Original Title",
            reviewed_by=reviewer,
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "title": "Updated Title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.title,
            "Updated Title",
        )

        self.assertEqual(
            request.reviewed_by,
            reviewer,
        )


    def test_staff_can_update_pending_request_without_changing_status(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Original Title",
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "title": "Updated by Staff",
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
            HRRequest.Status.PENDING,
        )

        self.assertEqual(
            request.title,
            "Updated by Staff",
        )

        self.assertIsNone(
            request.reviewed_by
        )

        self.assertIsNone(
            request.reviewed_at
        )


    def test_user_can_update_own_pending_request_fields(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Original Title",
            description="Original description.",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "title": "Updated Title",
                "description": "Updated description.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.title,
            "Updated Title",
        )

        self.assertEqual(
            request.description,
            "Updated description.",
        )

    def test_user_cannot_forge_requested_by(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {
                "employee": self.employee.id,
                "requested_by": self.staff.id,
                "request_type": HRRequest.RequestType.LEAVE,
                "title": "Forged Request",
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

        self.assertNotEqual(
            request.requested_by,
            self.staff,
        )


    def test_user_cannot_forge_reviewed_by(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {
                "employee": self.employee.id,
                "reviewed_by": self.staff.id,
                "reviewed_at": "2026-08-22T10:00:00Z",
                "request_type": HRRequest.RequestType.LEAVE,
                "title": "Forged Review",
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

        self.assertIsNone(
            request.reviewed_by
        )

        self.assertIsNone(
            request.reviewed_at
        )


    def test_user_cannot_modify_other_users_request(self):
        other_user = User.objects.create_user(
            username="other_user",
            password="StrongPassword123",
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=other_user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Other User Request",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "title": "Hacked Title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.title,
            "Other User Request",
        )


    def test_user_cannot_delete_other_users_request(self):
        other_user = User.objects.create_user(
            username="other_delete",
            password="StrongPassword123",
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=other_user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Protected Request",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            f"{self.url}{request.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            HRRequest.objects.filter(
                id=request.id
            ).exists()
        )


    def test_staff_cannot_modify_approved_request(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Approved Request",
            status=HRRequest.Status.APPROVED,
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "title": "Modified Approved Request",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.title,
            "Approved Request",
        )


    def test_invalid_status_is_rejected(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Invalid Status Test",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": "INVALID_STATUS",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            HRRequest.Status.PENDING,
        )


    def test_empty_title_is_rejected(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {
                "employee": self.employee.id,
                "request_type": HRRequest.RequestType.LEAVE,
                "title": "   ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "title",
            response.data,
        )


    def test_status_change_sets_reviewer_only_on_transition(self):
        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Reviewer Test",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "title": "Updated Title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertIsNone(
            request.reviewed_by
        )

        self.assertIsNone(
            request.reviewed_at
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.APPROVED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.reviewed_by,
            self.staff,
        )

        self.assertIsNotNone(
            request.reviewed_at
        )


    def test_user_cannot_change_employee_on_pending_request(self):
        another_employee = Employee.objects.create(
            first_name="Another",
            last_name="Employee",
            personnel_code="EMP-003",
            national_id="1234567891",
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Employee Protection",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "employee": another_employee.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.employee,
            self.employee,
        )

        self.assertNotEqual(
            request.employee,
            another_employee,
        )


    def test_user_cannot_change_request_type_on_pending_request(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Request Type Protection",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "request_type": HRRequest.RequestType.LOAN,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.request_type,
            HRRequest.RequestType.LEAVE,
        )

    def test_approval_creates_update_audit_log(self):
        from apps.audit.models import AuditLog

        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.APPROVED,
                "response": "Approved.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        audit = AuditLog.objects.filter(
            object_id=str(request.id),
            action=AuditLog.Action.UPDATE,
            app_label="requests",
            model_name="hrrequest",
        ).latest("id")

        self.assertEqual(
            audit.actor,
            self.staff,
        )

        self.assertEqual(
            audit.changes["status"]["old"],
            HRRequest.Status.PENDING,
        )

        self.assertEqual(
            audit.changes["status"]["new"],
            HRRequest.Status.APPROVED,
        )


    def test_rejection_creates_update_audit_log(self):
        from apps.audit.models import AuditLog

        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.REJECTED,
                "response": "Rejected.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        audit = AuditLog.objects.filter(
            object_id=str(request.id),
            action=AuditLog.Action.UPDATE,
            app_label="requests",
            model_name="hrrequest",
        ).latest("id")

        self.assertEqual(
            audit.actor,
            self.staff,
        )

        self.assertEqual(
            audit.changes["status"]["old"],
            HRRequest.Status.PENDING,
        )

        self.assertEqual(
            audit.changes["status"]["new"],
            HRRequest.Status.REJECTED,
        )


    def test_cancellation_creates_update_audit_log(self):
        from apps.audit.models import AuditLog

        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "status": HRRequest.Status.CANCELLED,
                "response": "Cancelled.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        audit = AuditLog.objects.filter(
            object_id=str(request.id),
            action=AuditLog.Action.UPDATE,
            app_label="requests",
            model_name="hrrequest",
        ).latest("id")

        self.assertEqual(
            audit.actor,
            self.staff,
        )

        self.assertEqual(
            audit.changes["status"]["old"],
            HRRequest.Status.PENDING,
        )

        self.assertEqual(
            audit.changes["status"]["new"],
            HRRequest.Status.CANCELLED,
        )

    def test_delete_pending_request_creates_delete_audit_log(self):
        from apps.audit.models import AuditLog

        self.client.force_authenticate(
            user=self.staff
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Request To Delete",
        )

        request_id = request.id

        response = self.client.delete(
            f"{self.url}{request_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            HRRequest.objects.filter(
                id=request_id
            ).exists()
        )

        audit = AuditLog.objects.filter(
            object_id=str(request_id),
            action=AuditLog.Action.DELETE,
            app_label="requests",
            model_name="hrrequest",
        ).latest("id")

        self.assertEqual(
            audit.actor,
            self.staff,
        )

        self.assertEqual(
            audit.object_id,
            str(request_id),
        )

    def test_user_cannot_override_requested_by_on_create(self):
        other_user = User.objects.create_user(
            username="other",
            password="StrongPassword123",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {
                "employee": self.employee.id,
                "requested_by": other_user.id,
                "request_type": HRRequest.RequestType.LEAVE,
                "title": "Annual Leave",
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

        self.assertNotEqual(
            request.requested_by,
            other_user,
        )


    def test_user_cannot_override_reviewed_by(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "reviewed_by": self.staff.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertIsNone(
            request.reviewed_by
        )


    def test_user_cannot_override_reviewed_at(self):
        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=self.user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Annual Leave",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{request.id}/",
            {
                "reviewed_at": "2030-01-01T12:00:00Z",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertIsNone(
            request.reviewed_at
        )


    def test_user_cannot_access_other_users_request_by_id(self):
        other_user = User.objects.create_user(
            username="other",
            password="StrongPassword123",
        )

        request = HRRequest.objects.create(
            employee=self.employee,
            requested_by=other_user,
            request_type=HRRequest.RequestType.LEAVE,
            title="Other User Request",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            f"{self.url}{request.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
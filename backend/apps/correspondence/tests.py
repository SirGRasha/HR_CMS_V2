from datetime import date

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.personnel.models import Employee

from .models import Correspondence
from .serializers import CorrespondenceSerializer


class CorrespondenceModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
        )

        self.employee = Employee.objects.create(
            personnel_code="EMP001",
            first_name="Reza",
            last_name="Test",
            gender=Employee.Gender.MALE,
            employee_group=Employee.EmployeeGroup.ADMINISTRATIVE,
            national_id="1234567890",
            marital_status=Employee.MaritalStatus.SINGLE,
        )

    def test_create_correspondence(self):
        correspondence = Correspondence.objects.create(
            correspondence_type=(
                Correspondence.CorrespondenceType.INCOMING
            ),
            letter_number="IN-001",
            letter_date=date(2026, 8, 22),
            subject="Test Letter",
            body="Test body.",
            sender="Company A",
            recipient="HR Department",
            employee=self.employee,
            created_by=self.user,
        )

        self.assertEqual(
            correspondence.status,
            Correspondence.Status.DRAFT,
        )

        self.assertEqual(
            correspondence.created_by,
            self.user,
        )

        self.assertEqual(
            correspondence.employee,
            self.employee,
        )

    def test_string_representation(self):
        correspondence = Correspondence.objects.create(
            correspondence_type=(
                Correspondence.CorrespondenceType.OUTGOING
            ),
            letter_number="OUT-001",
            letter_date=date(2026, 8, 22),
            subject="Official Letter",
            sender="HR",
            recipient="Employee",
            created_by=self.user,
        )

        self.assertEqual(
            str(correspondence),
            "OUT-001 - Official Letter",
        )

    def test_default_status_is_draft(self):
        correspondence = Correspondence.objects.create(
            correspondence_type=(
                Correspondence.CorrespondenceType.INTERNAL
            ),
            letter_number="INT-001",
            letter_date=date(2026, 8, 22),
            subject="Internal",
            sender="HR",
            recipient="Management",
            created_by=self.user,
        )

        self.assertEqual(
            correspondence.status,
            Correspondence.Status.DRAFT,
        )


class CorrespondenceSerializerTest(TestCase):

    def get_valid_data(self):
        return {
            "correspondence_type": "INCOMING",
            "letter_number": "IN-001",
            "letter_date": "2026-08-22",
            "subject": "Test Letter",
            "body": "Test body.",
            "sender": "Company A",
            "recipient": "HR Department",
        }

    def test_valid_data(self):
        serializer = CorrespondenceSerializer(
            data=self.get_valid_data()
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_empty_letter_number_is_invalid(self):
        data = self.get_valid_data()
        data["letter_number"] = "   "

        serializer = CorrespondenceSerializer(
            data=data
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "letter_number",
            serializer.errors,
        )

    def test_empty_subject_is_invalid(self):
        data = self.get_valid_data()
        data["subject"] = "   "

        serializer = CorrespondenceSerializer(
            data=data
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "subject",
            serializer.errors,
        )

    def test_empty_sender_is_invalid(self):
        data = self.get_valid_data()
        data["sender"] = "   "

        serializer = CorrespondenceSerializer(
            data=data
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "sender",
            serializer.errors,
        )

    def test_empty_recipient_is_invalid(self):
        data = self.get_valid_data()
        data["recipient"] = "   "

        serializer = CorrespondenceSerializer(
            data=data
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "recipient",
            serializer.errors,
        )

    def test_created_by_is_read_only(self):
        serializer = CorrespondenceSerializer(
            data=self.get_valid_data()
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertNotIn(
            "created_by",
            serializer.validated_data,
        )

    def test_display_fields_are_read_only(self):
        serializer = CorrespondenceSerializer(
            data=self.get_valid_data()
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertNotIn(
            "status_display",
            serializer.validated_data,
        )

        self.assertNotIn(
            "correspondence_type_display",
            serializer.validated_data,
        )


class CorrespondenceAPITest(APITestCase):

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
            personnel_code="EMP001",
            first_name="Reza",
            last_name="Test",
            gender=Employee.Gender.MALE,
            employee_group=Employee.EmployeeGroup.ADMINISTRATIVE,
            national_id="1234567890",
            marital_status=Employee.MaritalStatus.SINGLE,
        )

        self.url = (
            "/api/correspondence/correspondences/"
        )

    def create_correspondence(
        self,
        **kwargs,
    ):
        defaults = {
            "correspondence_type": (
                Correspondence.CorrespondenceType.INCOMING
            ),
            "letter_number": "IN-001",
            "letter_date": date(2026, 8, 22),
            "subject": "Test Letter",
            "body": "Test body.",
            "sender": "Company A",
            "recipient": "HR Department",
            "created_by": self.user,
        }

        defaults.update(kwargs)

        return Correspondence.objects.create(
            **defaults
        )

    def get_payload(self):
        return {
            "correspondence_type": "INCOMING",
            "letter_number": "IN-100",
            "letter_date": "2026-08-22",
            "subject": "New Letter",
            "body": "New body.",
            "sender": "Company A",
            "recipient": "HR Department",
        }

    def test_unauthenticated_user_cannot_list(self):
        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_create(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            self.get_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        correspondence = (
            Correspondence.objects.get(
                id=response.data["id"]
            )
        )

        self.assertEqual(
            correspondence.created_by,
            self.user,
        )

        self.assertEqual(
            correspondence.status,
            Correspondence.Status.DRAFT,
        )

    def test_user_can_list_correspondence(self):
        self.create_correspondence()

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
            1,
        )

    def test_user_can_retrieve_correspondence(self):
        correspondence = (
            self.create_correspondence()
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            f"{self.url}{correspondence.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            correspondence.id,
        )

    def test_normal_user_cannot_update(self):
        correspondence = (
            self.create_correspondence()
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "subject": "Changed",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_normal_user_cannot_delete(self):
        correspondence = (
            self.create_correspondence()
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            f"{self.url}{correspondence.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_staff_can_update(self):
        correspondence = (
            self.create_correspondence()
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "subject": "Updated Subject",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        correspondence.refresh_from_db()

        self.assertEqual(
            correspondence.subject,
            "Updated Subject",
        )

    def test_staff_can_delete(self):
        correspondence = (
            self.create_correspondence()
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.delete(
            f"{self.url}{correspondence.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Correspondence.objects.filter(
                id=correspondence.id
            ).exists()
        )

    def test_filter_by_type(self):
        self.create_correspondence(
            correspondence_type=(
                Correspondence.CorrespondenceType.INCOMING
            ),
            letter_number="IN-001",
        )

        self.create_correspondence(
            correspondence_type=(
                Correspondence.CorrespondenceType.OUTGOING
            ),
            letter_number="OUT-001",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.url,
            {
                "correspondence_type": "OUTGOING",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0][
                "correspondence_type"
            ],
            "OUTGOING",
        )

    def test_filter_by_status(self):
        self.create_correspondence(
            status=(
                Correspondence.Status.DRAFT
            ),
            letter_number="DRAFT-001",
        )

        self.create_correspondence(
            status=(
                Correspondence.Status.SENT
            ),
            letter_number="SENT-001",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.url,
            {
                "status": "SENT",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_filter_by_employee(self):
        self.create_correspondence(
            employee=self.employee,
            letter_number="EMP-001",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.url,
            {
                "employee": self.employee.id,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_filter_by_letter_number(self):
        self.create_correspondence(
            letter_number="ABC-12345"
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.url,
            {
                "letter_number": "12345",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_create_creates_audit_log(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            self.get_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        audit = AuditLog.objects.get(
            object_id=str(response.data["id"]),
            action=AuditLog.Action.CREATE,
        )

        self.assertEqual(
            audit.actor,
            self.user,
        )

        self.assertEqual(
            audit.app_label,
            "correspondence",
        )

        self.assertEqual(
            audit.model_name,
            "correspondence",
        )

    def test_update_creates_audit_log(self):
        correspondence = (
            self.create_correspondence()
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "subject": "Updated",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        audit = AuditLog.objects.get(
            object_id=str(correspondence.id),
            action=AuditLog.Action.UPDATE,
        )

        self.assertEqual(
            audit.actor,
            self.staff,
        )

        self.assertEqual(
            audit.changes["subject"]["old"],
            "Test Letter",
        )

        self.assertEqual(
            audit.changes["subject"]["new"],
            "Updated",
        )

    def test_delete_creates_audit_log(self):
        correspondence = (
            self.create_correspondence()
        )

        correspondence_id = correspondence.id

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.delete(
            f"{self.url}{correspondence_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        audit = AuditLog.objects.get(
            object_id=str(correspondence_id),
            action=AuditLog.Action.DELETE,
        )

        self.assertEqual(
            audit.actor,
            self.staff,
        )

    def test_created_by_cannot_be_forged_on_create(self):
        another_user = User.objects.create_user(
            username="another",
            password="StrongPassword123",
        )

        self.client.force_authenticate(
            user=self.user
        )

        payload = self.get_payload()
        payload["created_by"] = another_user.id

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        correspondence = Correspondence.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            correspondence.created_by,
            self.user,
        )

        self.assertNotEqual(
            correspondence.created_by,
            another_user,
        )

    def test_created_by_cannot_be_changed_on_update(self):
        correspondence = self.create_correspondence()

        another_user = User.objects.create_user(
            username="another_update",
            password="StrongPassword123",
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "created_by": another_user.id,
                "subject": "Updated Subject",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        correspondence.refresh_from_db()

        self.assertEqual(
            correspondence.created_by,
            self.user,
        )

    def test_invalid_correspondence_type_is_rejected(self):
        self.client.force_authenticate(
            user=self.user
        )

        payload = self.get_payload()
        payload["correspondence_type"] = "INVALID"

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_status_is_rejected(self):
        correspondence = self.create_correspondence()

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "status": "INVALID_STATUS",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_letter_number_only_spaces_is_rejected_on_api(self):
        self.client.force_authenticate(
            user=self.user
        )

        payload = self.get_payload()
        payload["letter_number"] = "   "

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_subject_only_spaces_is_rejected_on_api(self):
        self.client.force_authenticate(
            user=self.user
        )

        payload = self.get_payload()
        payload["subject"] = "   "

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_sender_only_spaces_is_rejected_on_api(self):
        self.client.force_authenticate(
            user=self.user
        )

        payload = self.get_payload()
        payload["sender"] = "   "

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_recipient_only_spaces_is_rejected_on_api(self):
        self.client.force_authenticate(
            user=self.user
        )

        payload = self.get_payload()
        payload["recipient"] = "   "

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_filter_by_multiple_fields(self):
        self.create_correspondence(
            correspondence_type=(
                Correspondence.CorrespondenceType.INCOMING
            ),
            status=Correspondence.Status.DRAFT,
            letter_number="IN-DRAFT-001",
        )

        self.create_correspondence(
            correspondence_type=(
                Correspondence.CorrespondenceType.INCOMING
            ),
            status=Correspondence.Status.SENT,
            letter_number="IN-SENT-001",
        )

        self.create_correspondence(
            correspondence_type=(
                Correspondence.CorrespondenceType.OUTGOING
            ),
            status=Correspondence.Status.DRAFT,
            letter_number="OUT-DRAFT-001",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.url,
            {
                "correspondence_type": "INCOMING",
                "status": "DRAFT",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["letter_number"],
            "IN-DRAFT-001",
        )

    def test_update_without_changes_does_not_create_audit_log(self):
        correspondence = self.create_correspondence()

        self.client.force_authenticate(
            user=self.staff
        )

        before_count = AuditLog.objects.filter(
            object_id=str(correspondence.id),
            action=AuditLog.Action.UPDATE,
        ).count()

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "subject": correspondence.subject,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        after_count = AuditLog.objects.filter(
            object_id=str(correspondence.id),
            action=AuditLog.Action.UPDATE,
        ).count()

        self.assertEqual(
            before_count,
            after_count,
        )

    def test_staff_can_register_draft_correspondence(self):
        correspondence = self.create_correspondence(
            status=Correspondence.Status.DRAFT
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "status": Correspondence.Status.REGISTERED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        correspondence.refresh_from_db()

        self.assertEqual(
            correspondence.status,
            Correspondence.Status.REGISTERED,
        )


    def test_staff_can_send_registered_correspondence(self):
        correspondence = self.create_correspondence(
            status=Correspondence.Status.REGISTERED
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "status": Correspondence.Status.SENT,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        correspondence.refresh_from_db()

        self.assertEqual(
            correspondence.status,
            Correspondence.Status.SENT,
        )


    def test_staff_can_receive_registered_correspondence(self):
        correspondence = self.create_correspondence(
            status=Correspondence.Status.REGISTERED
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "status": Correspondence.Status.RECEIVED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        correspondence.refresh_from_db()

        self.assertEqual(
            correspondence.status,
            Correspondence.Status.RECEIVED,
        )


    def test_staff_can_archive_sent_correspondence(self):
        correspondence = self.create_correspondence(
            status=Correspondence.Status.SENT
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "status": Correspondence.Status.ARCHIVED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        correspondence.refresh_from_db()

        self.assertEqual(
            correspondence.status,
            Correspondence.Status.ARCHIVED,
        )


    def test_staff_can_archive_received_correspondence(self):
        correspondence = self.create_correspondence(
            status=Correspondence.Status.RECEIVED
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "status": Correspondence.Status.ARCHIVED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        correspondence.refresh_from_db()

        self.assertEqual(
            correspondence.status,
            Correspondence.Status.ARCHIVED,
        )

    def test_cannot_skip_from_draft_to_archived(self):
        correspondence = self.create_correspondence(
            status=Correspondence.Status.DRAFT
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "status": Correspondence.Status.ARCHIVED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def test_cannot_move_registered_back_to_draft(self):
        correspondence = self.create_correspondence(
            status=Correspondence.Status.REGISTERED
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "status": Correspondence.Status.DRAFT,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def test_cannot_move_archived_correspondence_back(self):
        correspondence = self.create_correspondence(
            status=Correspondence.Status.ARCHIVED
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "status": Correspondence.Status.DRAFT,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def test_cannot_move_sent_back_to_registered(self):
        correspondence = self.create_correspondence(
            status=Correspondence.Status.SENT
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "status": Correspondence.Status.REGISTERED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


    def test_cannot_move_received_to_sent(self):
        correspondence = self.create_correspondence(
            status=Correspondence.Status.RECEIVED
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "status": Correspondence.Status.SENT,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_staff_can_update_correspondence_without_changing_status(self):
        correspondence = self.create_correspondence(
            status=Correspondence.Status.REGISTERED
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            f"{self.url}{correspondence.id}/",
            {
                "subject": "Updated Subject",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        correspondence.refresh_from_db()

        self.assertEqual(
            correspondence.subject,
            "Updated Subject",
        )

        self.assertEqual(
            correspondence.status,
            Correspondence.Status.REGISTERED,
        )
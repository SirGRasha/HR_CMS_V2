from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User

from .models import Notification


class NotificationModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
        )

    def test_create_notification(self):
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=Notification.NotificationType.INFO,
            title="Test Notification",
            message="This is a test notification.",
        )

        self.assertEqual(
            notification.recipient,
            self.user,
        )

        self.assertEqual(
            notification.notification_type,
            Notification.NotificationType.INFO,
        )

        self.assertFalse(
            notification.is_read
        )

        self.assertIsNone(
            notification.read_at
        )

    def test_notification_string(self):
        notification = Notification.objects.create(
            recipient=self.user,
            title="Test Notification",
            message="Test message.",
        )

        self.assertEqual(
            str(notification),
            "reza - Test Notification",
        )

class NotificationSerializerTest(TestCase):

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

    def get_valid_data(self):
        return {
            "recipient": self.user.id,
            "notification_type": "INFO",
            "title": "Test Notification",
            "message": "Test message.",
            "link": "/test/",
            "related_model": "TestModel",
            "related_object_id": "1",
        }

    def test_empty_title_is_invalid(self):
        from .serializers import NotificationSerializer

        data = self.get_valid_data()
        data["title"] = "   "

        serializer = NotificationSerializer(
            data=data
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "title",
            serializer.errors,
        )

    def test_display_field_is_read_only(self):
        from .serializers import NotificationSerializer

        serializer = NotificationSerializer(
            data=self.get_valid_data()
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertNotIn(
            "notification_type_display",
            serializer.validated_data,
        )

    def test_read_at_is_read_only(self):
        from .serializers import NotificationSerializer

        serializer = NotificationSerializer(
            data={
                **self.get_valid_data(),
                "read_at": "2026-08-22T10:00:00Z",
            }
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertNotIn(
            "read_at",
            serializer.validated_data,
        )

class NotificationServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="service_user",
            password="StrongPassword123",
        )

    def test_create_notification(self):
        from .services.notification_service import (
            NotificationService,
        )

        notification = NotificationService.create(
            recipient=self.user,
            notification_type=(
                Notification.NotificationType.REQUEST
            ),
            title="Request Updated",
            message="Your request was updated.",
            link="/api/requests/requests/1/",
            related_model="HRRequest",
            related_object_id="1",
        )

        self.assertIsNotNone(
            notification.id
        )

        self.assertEqual(
            notification.recipient,
            self.user,
        )

        self.assertEqual(
            notification.notification_type,
            Notification.NotificationType.REQUEST,
        )

        self.assertEqual(
            notification.title,
            "Request Updated",
        )

        self.assertEqual(
            notification.message,
            "Your request was updated.",
        )

        self.assertEqual(
            notification.link,
            "/api/requests/requests/1/",
        )

        self.assertEqual(
            notification.related_model,
            "HRRequest",
        )

        self.assertEqual(
            notification.related_object_id,
            "1",
        )

        self.assertFalse(
            notification.is_read
        )
        
class NotificationAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
        )

        self.other_user = User.objects.create_user(
            username="other",
            password="StrongPassword123",
        )

        self.staff = User.objects.create_user(
            username="staff",
            password="StrongPassword123",
            is_staff=True,
        )

        self.superuser = User.objects.create_user(
            username="admin",
            password="StrongPassword123",
            is_staff=True,
            is_superuser=True,
        )

        self.url = "/api/notifications/notifications/"

    def create_notification(
        self,
        recipient=None,
        **kwargs,
    ):
        return Notification.objects.create(
            recipient=recipient or self.user,
            notification_type=kwargs.get(
                "notification_type",
                Notification.NotificationType.INFO,
            ),
            title=kwargs.get(
                "title",
                "Test Notification",
            ),
            message=kwargs.get(
                "message",
                "Test message.",
            ),
            is_read=kwargs.get(
                "is_read",
                False,
            ),
        )

    def test_unauthenticated_user_cannot_list_notifications(
        self,
    ):
        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_list_own_notifications(self):
        self.create_notification()

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

    def test_user_cannot_see_other_users_notifications(
        self,
    ):
        self.create_notification(
            recipient=self.other_user
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

    def test_staff_can_list_all_notifications(self):
        self.create_notification()

        self.create_notification(
            recipient=self.other_user
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
            2,
        )

    def test_user_cannot_create_notification(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {
                "recipient": self.user.id,
                "notification_type": "INFO",
                "title": "Test",
                "message": "Test message.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_staff_can_create_notification(self):
        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.post(
            self.url,
            {
                "recipient": self.user.id,
                "notification_type": "REQUEST",
                "title": "Request Update",
                "message": "Your request was updated.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        notification = Notification.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            notification.recipient,
            self.user,
        )

    def test_user_can_mark_own_notification_as_read(
        self,
    ):
        notification = self.create_notification()

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{notification.id}/",
            {
                "is_read": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notification.refresh_from_db()

        self.assertTrue(
            notification.is_read
        )

        self.assertIsNotNone(
            notification.read_at
        )

    def test_user_can_mark_notification_as_unread(
        self,
    ):
        notification = self.create_notification(
            is_read=True
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{notification.id}/",
            {
                "is_read": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notification.refresh_from_db()

        self.assertFalse(
            notification.is_read
        )

        self.assertIsNone(
            notification.read_at
        )

    def test_user_cannot_modify_other_users_notification(
        self,
    ):
        notification = self.create_notification(
            recipient=self.other_user
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{notification.id}/",
            {
                "is_read": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_can_delete_own_notification(self):
        notification = self.create_notification()

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            f"{self.url}{notification.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Notification.objects.filter(
                id=notification.id
            ).exists()
        )

    def test_user_cannot_delete_other_users_notification(
        self,
    ):
        notification = self.create_notification(
            recipient=self.other_user
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.delete(
            f"{self.url}{notification.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_filter_by_read_status(self):
        self.create_notification(
            is_read=False
        )

        self.create_notification(
            is_read=True
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.url,
            {
                "is_read": "false",
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

    def test_filter_by_notification_type(self):
        self.create_notification(
            notification_type=(
                Notification.NotificationType.REQUEST
            )
        )

        self.create_notification(
            notification_type=(
                Notification.NotificationType.PAYROLL
            )
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.url,
            {
                "notification_type": "REQUEST",
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

    def test_user_can_mark_own_notification_using_read_action(self):
        notification = self.create_notification()

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            f"{self.url}{notification.id}/read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notification.refresh_from_db()

        self.assertTrue(
            notification.is_read
        )

        self.assertIsNotNone(
            notification.read_at
        )

    def test_mark_read_action_is_idempotent(self):
        notification = self.create_notification(
            is_read=True
        )

        self.client.force_authenticate(
            user=self.user
        )

        old_read_at = notification.read_at

        response = self.client.post(
            f"{self.url}{notification.id}/read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notification.refresh_from_db()

        self.assertTrue(
            notification.is_read
        )

        self.assertIsNotNone(
            notification.read_at
        )

    def test_user_can_mark_all_own_notifications_as_read(self):
        notification_1 = self.create_notification(
            title="Notification 1"
        )

        notification_2 = self.create_notification(
            title="Notification 2"
        )

        self.create_notification(
            recipient=self.other_user,
            title="Other User Notification",
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            f"{self.url}mark-all-read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["updated_count"],
            2,
        )

        notification_1.refresh_from_db()
        notification_2.refresh_from_db()

        self.assertTrue(
            notification_1.is_read
        )

        self.assertTrue(
            notification_2.is_read
        )

        self.assertIsNotNone(
            notification_1.read_at
        )

        self.assertIsNotNone(
            notification_2.read_at
        )

        other_notification = Notification.objects.get(
            recipient=self.other_user,
            title="Other User Notification",
        )

        self.assertFalse(
            other_notification.is_read
        )

    def test_mark_all_read_only_affects_unread_notifications(self):
        unread = self.create_notification(
            title="Unread"
        )

        read = self.create_notification(
            title="Already Read",
            is_read=True,
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            f"{self.url}mark-all-read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["updated_count"],
            1,
        )

        unread.refresh_from_db()
        read.refresh_from_db()

        self.assertTrue(
            unread.is_read
        )

        self.assertTrue(
            read.is_read
        )

    def test_mark_all_read_with_no_unread_returns_zero(self):
        self.create_notification(
            is_read=True
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            f"{self.url}mark-all-read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["updated_count"],
            0,
        )

    def test_user_cannot_mark_other_users_notification_as_read(self):
        notification = self.create_notification(
            recipient=self.other_user
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            f"{self.url}{notification.id}/read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        notification.refresh_from_db()

        self.assertFalse(
            notification.is_read
        )

    def test_staff_can_mark_notification_as_read(self):
        notification = self.create_notification()

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.post(
            f"{self.url}{notification.id}/read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notification.refresh_from_db()

        self.assertTrue(
            notification.is_read
        )

        self.assertIsNotNone(
            notification.read_at
        )

    def test_staff_can_mark_all_notifications_as_read(self):
        self.create_notification(
            recipient=self.user
        )

        self.create_notification(
            recipient=self.other_user
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.post(
            f"{self.url}mark-all-read/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["updated_count"],
            2,
        )

        self.assertFalse(
            Notification.objects.filter(
                is_read=False
            ).exists()
        )

    def test_user_cannot_create_notification_even_if_forging_recipient(self):
        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.post(
            self.url,
            {
                "recipient": self.other_user.id,
                "notification_type": "INFO",
                "title": "Forged Notification",
                "message": "This should fail.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertFalse(
            Notification.objects.filter(
                title="Forged Notification"
            ).exists()
        )

    def test_staff_can_create_notification_for_any_user(self):
        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.post(
            self.url,
            {
                "recipient": self.other_user.id,
                "notification_type": "WARNING",
                "title": "Important",
                "message": "Important notification.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        notification = Notification.objects.get(
            id=response.data["id"]
        )

        self.assertEqual(
            notification.recipient,
            self.other_user,
        )

    def test_invalid_empty_title_is_rejected(self):
        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.post(
            self.url,
            {
                "recipient": self.user.id,
                "notification_type": "INFO",
                "title": "   ",
                "message": "Test message.",
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

    def test_invalid_is_read_filter_is_ignored(self):
        self.create_notification(
            is_read=False
        )

        self.create_notification(
            is_read=True
        )

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.get(
            self.url,
            {
                "is_read": "invalid",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )

    def test_user_cannot_modify_notification_content(self):
        notification = self.create_notification()

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{notification.id}/",
            {
                "title": "Forged Title",
                "message": "Forged Message",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        notification.refresh_from_db()

        self.assertEqual(
            notification.title,
            "Test Notification",
        )

        self.assertEqual(
            notification.message,
            "Test message.",
        )


    def test_user_can_change_only_is_read(self):
        notification = self.create_notification()

        self.client.force_authenticate(
            user=self.user
        )

        response = self.client.patch(
            f"{self.url}{notification.id}/",
            {
                "is_read": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notification.refresh_from_db()

        self.assertTrue(
            notification.is_read
        )

        self.assertIsNotNone(
            notification.read_at
        )
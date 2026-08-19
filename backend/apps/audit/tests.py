from rest_framework import status
from rest_framework.test import APITestCase

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.audit.services import AuditService


class AuditServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="audit_user",
            password="StrongPassword123",
        )

        self.target_user = User.objects.create_user(
            username="target_user",
            password="StrongPassword123",
        )

        self.factory = APIRequestFactory()

        self.request = self.factory.get(
            "/api/test/",
            HTTP_X_FORWARDED_FOR="192.168.1.100, 10.0.0.1",
            HTTP_USER_AGENT="HR-CG-Test-Agent",
        )

    def test_create_audit_log(self):
        audit = AuditService.create(
            actor=self.user,
            instance=self.target_user,
            request=self.request,
            changes={
                "username": {
                    "old": None,
                    "new": "target_user",
                }
            },
        )

        self.assertIsNotNone(audit.pk)
        self.assertEqual(
            audit.actor,
            self.user,
        )
        self.assertEqual(
            audit.action,
            AuditLog.Action.CREATE,
        )
        self.assertEqual(
            audit.app_label,
            "accounts",
        )
        self.assertEqual(
            audit.model_name,
            "user",
        )
        self.assertEqual(
            audit.object_id,
            str(self.target_user.id),
        )

    def test_update_audit_log(self):
        changes = {
            "first_name": {
                "old": "",
                "new": "Reza",
            }
        }

        audit = AuditService.update(
            actor=self.user,
            instance=self.target_user,
            request=self.request,
            changes=changes,
        )

        self.assertEqual(
            audit.action,
            AuditLog.Action.UPDATE,
        )

        self.assertEqual(
            audit.changes,
            changes,
        )

    def test_delete_audit_log(self):
        audit = AuditService.delete(
            actor=self.user,
            instance=self.target_user,
            request=self.request,
        )

        self.assertEqual(
            audit.action,
            AuditLog.Action.DELETE,
        )

        self.assertEqual(
            audit.object_id,
            str(self.target_user.id),
        )

    def test_login_audit_log(self):
        audit = AuditService.login(
            actor=self.user,
            instance=self.user,
            request=self.request,
        )

        self.assertEqual(
            audit.action,
            AuditLog.Action.LOGIN,
        )

        self.assertEqual(
            audit.actor,
            self.user,
        )

    def test_logout_audit_log(self):
        audit = AuditService.logout(
            actor=self.user,
            instance=self.user,
            request=self.request,
        )

        self.assertEqual(
            audit.action,
            AuditLog.Action.LOGOUT,
        )

    def test_password_change_audit_log(self):
        audit = AuditService.password_change(
            actor=self.user,
            instance=self.user,
            request=self.request,
        )

        self.assertEqual(
            audit.action,
            AuditLog.Action.PASSWORD_CHANGE,
        )

    def test_ip_address_from_forwarded_for(self):
        audit = AuditService.create(
            actor=self.user,
            instance=self.target_user,
            request=self.request,
        )

        self.assertEqual(
            audit.ip_address,
            "192.168.1.100",
        )

    def test_user_agent_is_stored(self):
        audit = AuditService.create(
            actor=self.user,
            instance=self.target_user,
            request=self.request,
        )

        self.assertEqual(
            audit.user_agent,
            "HR-CG-Test-Agent",
        )

    def test_direct_ip_is_used_when_forwarded_for_is_missing(self):
        request = self.factory.get(
            "/api/test/",
            REMOTE_ADDR="127.0.0.1",
            HTTP_USER_AGENT="Direct-Agent",
        )

        audit = AuditService.create(
            actor=self.user,
            instance=self.target_user,
            request=request,
        )

        self.assertEqual(
            audit.ip_address,
            "127.0.0.1",
        )

    def test_empty_changes_are_stored_as_empty_dict(self):
        audit = AuditService.create(
            actor=self.user,
            instance=self.target_user,
            request=self.request,
        )

        self.assertEqual(
            audit.changes,
            {},
        )

    def test_anonymous_actor_is_allowed(self):
        audit = AuditService.create(
            actor=None,
            instance=self.target_user,
            request=self.request,
        )

        self.assertIsNone(
            audit.actor,
        )

    def test_without_request(self):
        audit = AuditService.create(
            actor=self.user,
            instance=self.target_user,
        )

        self.assertIsNone(
            audit.ip_address,
        )

        self.assertEqual(
            audit.user_agent,
            "",
        )

    def test_multiple_audit_logs_are_created(self):
        AuditService.create(
            actor=self.user,
            instance=self.target_user,
        )

        AuditService.update(
            actor=self.user,
            instance=self.target_user,
        )

        AuditService.delete(
            actor=self.user,
            instance=self.target_user,
        )

        self.assertEqual(
            AuditLog.objects.count(),
            3,
        )

class AuditLogAPITest(APITestCase):

    def setUp(self):
        self.normal_user = User.objects.create_user(
            username="normal",
            password="StrongPassword123",
        )

        self.staff_user = User.objects.create_user(
            username="staff",
            password="StrongPassword123",
            is_staff=True,
        )

        self.superuser = User.objects.create_superuser(
            username="admin",
            password="StrongPassword123",
        )

        self.audit = AuditLog.objects.create(
            actor=self.staff_user,
            action=AuditLog.Action.UPDATE,
            app_label="accounts",
            model_name="user",
            object_id="1",
            object_repr="normal",
            changes={
                "first_name": {
                    "old": "Old",
                    "new": "New",
                }
            },
            ip_address="192.168.1.100",
            user_agent="HR-CG-Test-Agent",
        )

        self.audit_url = "/api/audit/"

    def test_search_by_object_repr(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.get(
            self.audit_url,
            {
                "search": "normal",
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
            response.data["results"][0]["object_repr"],
            "normal",
        )

    def test_search_by_actor_username(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.get(
            self.audit_url,
            {
                "search": "staff",
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
            response.data["results"][0]["actor_username"],
            "staff",
        )

    def test_search_by_actor_first_name(self):
        self.staff_user.first_name = "Reza"
        self.staff_user.save(
            update_fields=["first_name"]
        )

        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.get(
            self.audit_url,
            {
                "search": "Reza",
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
            response.data["results"][0]["actor_username"],
            "staff",
        )

    def test_search_without_results_returns_empty(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.get(
            self.audit_url,
            {
                "search": "DoesNotExist",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            0,
        )

        self.assertEqual(
            response.data["results"],
            [],
        )

        self.audit_url = "/api/audit/"

    def test_normal_user_cannot_view_audit_logs(self):
        self.client.force_authenticate(
            user=self.normal_user
        )

        response = self.client.get(
            self.audit_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_staff_can_view_audit_logs(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.get(
            self.audit_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_superuser_can_view_audit_logs(self):
        self.client.force_authenticate(
            user=self.superuser
        )

        response = self.client.get(
            self.audit_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_unauthenticated_user_cannot_view_audit_logs(self):
        response = self.client.get(
            self.audit_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_audit_log_detail_is_read_only(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.get(
            f"{self.audit_url}{self.audit.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["action"],
            AuditLog.Action.UPDATE,
        )

    def test_audit_log_create_is_not_allowed(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.post(
            self.audit_url,
            {
                "action": AuditLog.Action.CREATE,
                "app_label": "accounts",
                "model_name": "user",
                "object_id": "999",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_audit_log_update_is_not_allowed(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.patch(
            f"{self.audit_url}{self.audit.id}/",
            {
                "object_repr": "Modified",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_audit_log_delete_is_not_allowed(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.delete(
            f"{self.audit_url}{self.audit.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_filter_by_actor(self):
        other_user = User.objects.create_user(
            username="other",
            password="StrongPassword123",
        )

        AuditLog.objects.create(
            actor=other_user,
            action=AuditLog.Action.CREATE,
            app_label="personnel",
            model_name="employee",
            object_id="2",
            object_repr="other",
        )

        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.get(
            self.audit_url,
            {
                "actor": self.staff_user.id,
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
            response.data["results"][0]["actor"],
            self.staff_user.id,
        )

    def test_filter_by_action(self):
        AuditLog.objects.create(
            actor=self.staff_user,
            action=AuditLog.Action.CREATE,
            app_label="personnel",
            model_name="employee",
            object_id="2",
            object_repr="employee",
        )

        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.get(
            self.audit_url,
            {
                "action": AuditLog.Action.CREATE,
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
            response.data["results"][0]["action"],
            AuditLog.Action.CREATE,
        )

    def test_filter_by_app_label(self):
        AuditLog.objects.create(
            actor=self.staff_user,
            action=AuditLog.Action.CREATE,
            app_label="personnel",
            model_name="employee",
            object_id="2",
            object_repr="employee",
        )

        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.get(
            self.audit_url,
            {
                "app_label": "personnel",
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
            response.data["results"][0]["app_label"],
            "personnel",
        )

    def test_filter_by_model_name(self):
        AuditLog.objects.create(
            actor=self.staff_user,
            action=AuditLog.Action.CREATE,
            app_label="personnel",
            model_name="employee",
            object_id="2",
            object_repr="employee",
        )

        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.get(
            self.audit_url,
            {
                "model_name": "employee",
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
            response.data["results"][0]["model_name"],
            "employee",
        )

    def test_filter_by_object_id(self):
        AuditLog.objects.create(
            actor=self.staff_user,
            action=AuditLog.Action.CREATE,
            app_label="personnel",
            model_name="employee",
            object_id="999",
            object_repr="employee",
        )

        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.get(
            self.audit_url,
            {
                "object_id": "999",
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
            response.data["results"][0]["object_id"],
            "999",
        )
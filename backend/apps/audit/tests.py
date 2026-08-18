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

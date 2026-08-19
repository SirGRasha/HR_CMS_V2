from django.test import TestCase

from apps.accounts.models import User
from apps.audit.models import AuditLog

from rest_framework import status
from rest_framework.test import APITestCase


class UserModelTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
            first_name="Reza",
            last_name="Test",
            email="reza@example.com",
        )

        self.assertEqual(user.username, "reza")
        self.assertEqual(user.first_name, "Reza")
        self.assertEqual(user.last_name, "Test")
        self.assertEqual(user.email, "reza@example.com")

    def test_password_is_hashed(self):
        user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
        )

        self.assertNotEqual(
            user.password,
            "StrongPassword123",
        )

        self.assertTrue(
            user.check_password("StrongPassword123")
        )

    def test_user_is_active_by_default(self):
        user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
        )

        self.assertTrue(user.is_active)

    def test_username_must_be_unique(self):
        User.objects.create_user(
            username="reza",
            password="StrongPassword123",
        )

        with self.assertRaises(Exception):
            User.objects.create_user(
                username="reza",
                password="AnotherPassword123",
            )

class MeAPIViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
            first_name="Reza",
            last_name="Test",
            email="reza@example.com",
        )

        self.url = "/api/accounts/me/"

    def test_unauthenticated_user_cannot_access_me(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_access_me(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_me_returns_current_user_data(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.data["id"],
            self.user.id,
        )

        self.assertEqual(
            response.data["username"],
            "reza",
        )

        self.assertEqual(
            response.data["first_name"],
            "Reza",
        )

        self.assertEqual(
            response.data["last_name"],
            "Test",
        )

        self.assertEqual(
            response.data["email"],
            "reza@example.com",
        )

    def test_password_is_not_exposed(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertNotIn(
            "password",
            response.data,
        )

    def test_me_returns_account_status(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.data["is_active"],
            True,
        )

        self.assertEqual(
            response.data["is_staff"],
            False,
        )

        self.assertEqual(
            response.data["is_superuser"],
            False,
        )
class JWTAuthenticationTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
            first_name="Reza",
            last_name="Test",
            email="reza@example.com",
        )

        self.token_url = "/api/accounts/token/"
        self.refresh_url = "/api/accounts/token/refresh/"
        self.me_url = "/api/accounts/me/"

    def test_login_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            self.token_url,
            {
                "username": "reza",
                "password": "StrongPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

        self.assertIn(
            "refresh",
            response.data,
        )

    def test_successful_login_creates_audit_log(self):
        from apps.audit.models import AuditLog

        response = self.client.post(
            self.token_url,
            {
                "username": "reza",
                "password": "StrongPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        audit = AuditLog.objects.filter(
            actor=self.user,
            action=AuditLog.Action.LOGIN,
            object_id=str(self.user.id),
        ).latest("created_at")

        self.assertEqual(
            audit.action,
            AuditLog.Action.LOGIN,
        )

        self.assertEqual(
            audit.actor,
            self.user,
        )

        self.assertEqual(
            audit.object_id,
            str(self.user.id),
        )

    def test_failed_login_does_not_create_audit_log(self):
        from apps.audit.models import AuditLog

        response = self.client.post(
            self.token_url,
            {
                "username": "reza",
                "password": "WrongPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertFalse(
            AuditLog.objects.filter(
                actor=self.user,
                action=AuditLog.Action.LOGIN,
            ).exists()
        )

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(
            self.token_url,
            {
                "username": "reza",
                "password": "WrongPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_login_with_unknown_user_fails(self):
        response = self.client.post(
            self.token_url,
            {
                "username": "unknown_user",
                "password": "StrongPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_access_token_can_authenticate_me(self):
        response = self.client.post(
            self.token_url,
            {
                "username": "reza",
                "password": "StrongPassword123",
            },
            format="json",
        )

        access_token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["username"],
            "reza",
        )

    def test_refresh_token_returns_new_access_token(self):
        response = self.client.post(
            self.token_url,
            {
                "username": "reza",
                "password": "StrongPassword123",
            },
            format="json",
        )

        refresh_token = response.data["refresh"]

        response = self.client.post(
            self.refresh_url,
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

class UserManagementAPITest(APITestCase):

    def setUp(self):
        self.normal_user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
            first_name="Reza",
            last_name="Test",
            email="reza@example.com",
        )

        self.staff_user = User.objects.create_user(
            username="staff",
            password="StrongPassword123",
            is_staff=True,
        )

        self.superuser = User.objects.create_superuser(
            username="admin",
            password="StrongPassword123",
            email="admin@example.com",
        )

        self.url = "/api/accounts/users/"

    def test_unauthenticated_user_cannot_list_users(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_normal_user_cannot_list_users(self):
        self.client.force_authenticate(user=self.normal_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_staff_can_list_users(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_staff_can_create_user(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.post(
            self.url,
            {
                "username": "newuser",
                "password": "NewStrongPassword123",
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(username="newuser")

        self.assertTrue(
            user.check_password("NewStrongPassword123")
        )

    def test_password_is_not_returned_when_creating_user(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.post(
            self.url,
            {
                "username": "newuser",
                "password": "NewStrongPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertNotIn(
            "password",
            response.data,
        )

    def test_staff_cannot_create_superuser(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.post(
            self.url,
            {
                "username": "evil_admin",
                "password": "StrongPassword123",
                "is_superuser": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_staff_cannot_create_staff_user(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.post(
            self.url,
            {
                "username": "another_staff",
                "password": "StrongPassword123",
                "is_staff": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_superuser_can_create_staff_user(self):
        self.client.force_authenticate(user=self.superuser)

        response = self.client.post(
            self.url,
            {
                "username": "new_staff",
                "password": "StrongPassword123",
                "is_staff": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(username="new_staff")

        self.assertTrue(user.is_staff)

    def test_staff_can_update_user(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.patch(
            f"{self.url}{self.normal_user.id}/",
            {
                "first_name": "Updated",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.normal_user.refresh_from_db()

        self.assertEqual(
            self.normal_user.first_name,
            "Updated",
        )

    def test_staff_cannot_change_superuser_flag(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.patch(
            f"{self.url}{self.normal_user.id}/",
            {
                "is_superuser": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_superuser_can_delete_user(self):
        self.client.force_authenticate(user=self.superuser)

        response = self.client.delete(
            f"{self.url}{self.normal_user.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            User.objects.filter(
                id=self.normal_user.id
            ).exists()
        )

    def test_staff_cannot_delete_user(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.delete(
            f"{self.url}{self.normal_user.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )


class UserPasswordAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="reza",
            password="OldPassword123",
        )

        self.other_user = User.objects.create_user(
            username="other",
            password="OtherPassword123",
        )

        self.staff_user = User.objects.create_user(
            username="staff",
            password="StaffPassword123",
            is_staff=True,
        )

        self.normal_user_url = (
            f"/api/accounts/users/{self.user.id}/password/"
        )

    def test_staff_cannot_change_another_staff_password(self):
        other_staff = User.objects.create_user(
            username="other_staff_password",
            password="OtherStaffPassword123",
            is_staff=True,
        )

        self.client.force_authenticate(
            user=self.staff_user
        )

        url = (
            f"/api/accounts/users/"
            f"{other_staff.id}/password/"
        )

        response = self.client.post(
            url,
            {
                "new_password": "HackedPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        other_staff.refresh_from_db()

        self.assertTrue(
            other_staff.check_password(
                "OtherStaffPassword123"
            )
        )

        self.assertFalse(
            other_staff.check_password(
                "HackedPassword123"
            )
        )

    def test_staff_cannot_change_superuser_password(self):
        superuser = User.objects.create_superuser(
            username="password_admin",
            password="AdminPassword123",
        )

        self.client.force_authenticate(
            user=self.staff_user
        )

        url = (
            f"/api/accounts/users/"
            f"{superuser.id}/password/"
        )

        response = self.client.post(
            url,
            {
                "new_password": "HackedPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        superuser.refresh_from_db()

        self.assertTrue(
            superuser.check_password(
                "AdminPassword123"
            )
        )

        self.assertFalse(
            superuser.check_password(
                "HackedPassword123"
            )
        )

    def test_user_can_change_own_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.normal_user_url,
            {
                "new_password": "NewPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password("NewPassword123")
        )

    def test_user_cannot_change_another_users_password(self):
        self.client.force_authenticate(user=self.user)

        url = (
            f"/api/accounts/users/"
            f"{self.other_user.id}/password/"
        )

        response = self.client.post(
            url,
            {
                "new_password": "HackedPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_staff_can_change_user_password(self):
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.post(
            self.normal_user_url,
            {
                "new_password": "ChangedByStaff123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "ChangedByStaff123"
            )
        )

    def test_password_is_not_returned(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.normal_user_url,
            {
                "new_password": "NewPassword123",
            },
            format="json",
        )

        self.assertNotIn(
            "password",
            response.data,
        )

    def test_superuser_can_change_staff_password(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        # ابتدا با یک superuser واقعی احراز هویت می‌کنیم.
        superuser = User.objects.create_superuser(
            username="password_superuser",
            password="AdminPassword123",
        )

        self.client.force_authenticate(
            user=superuser
        )

        url = (
            f"/api/accounts/users/"
            f"{self.staff_user.id}/password/"
        )

        response = self.client.post(
            url,
            {
                "new_password": "ChangedByAdmin123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.staff_user.refresh_from_db()

        self.assertTrue(
            self.staff_user.check_password(
                "ChangedByAdmin123"
            )
        )

class UserSecurityAPITest(APITestCase):

    def setUp(self):
        self.normal_user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
        )

        self.staff_user = User.objects.create_user(
            username="staff",
            password="StrongPassword123",
            is_staff=True,
        )

        self.other_staff = User.objects.create_user(
            username="other_staff",
            password="StrongPassword123",
            is_staff=True,
        )

        self.superuser = User.objects.create_superuser(
            username="admin",
            password="StrongPassword123",
        )

        self.users_url = "/api/accounts/users/"

    def test_staff_cannot_promote_self_to_superuser(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.patch(
            f"{self.users_url}{self.staff_user.id}/",
            {
                "is_superuser": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.staff_user.refresh_from_db()

        self.assertFalse(
            self.staff_user.is_superuser
        )

    def test_staff_cannot_promote_self_to_staff_against_policy(self):
        self.client.force_authenticate(
            user=self.normal_user
        )

        response = self.client.patch(
            f"{self.users_url}{self.normal_user.id}/",
            {
                "is_staff": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.normal_user.refresh_from_db()

        self.assertFalse(
            self.normal_user.is_staff
        )

    def test_staff_cannot_modify_superuser(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.patch(
            f"{self.users_url}{self.superuser.id}/",
            {
                "first_name": "Hacked",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.superuser.refresh_from_db()

        self.assertNotEqual(
            self.superuser.first_name,
            "Hacked",
        )

    def test_staff_cannot_delete_superuser(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.delete(
            f"{self.users_url}{self.superuser.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            User.objects.filter(
                id=self.superuser.id
            ).exists()
        )

    def test_superuser_can_modify_staff_status(self):
        self.client.force_authenticate(
            user=self.superuser
        )

        response = self.client.patch(
            f"{self.users_url}{self.normal_user.id}/",
            {
                "is_staff": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.normal_user.refresh_from_db()

        self.assertTrue(
            self.normal_user.is_staff
        )

    def test_superuser_can_promote_user_to_superuser(self):
        self.client.force_authenticate(
            user=self.superuser
        )

        response = self.client.patch(
            f"{self.users_url}{self.normal_user.id}/",
            {
                "is_superuser": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.normal_user.refresh_from_db()

        self.assertTrue(
            self.normal_user.is_superuser
        )

    def test_normal_user_cannot_access_user_detail(self):
        self.client.force_authenticate(
            user=self.normal_user
        )

        response = self.client.get(
            f"{self.users_url}{self.staff_user.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_normal_user_cannot_change_another_user(self):
        self.client.force_authenticate(
            user=self.normal_user
        )

        response = self.client.patch(
            f"{self.users_url}{self.staff_user.id}/",
            {
                "first_name": "Hacked",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_normal_user_cannot_delete_any_user(self):
        self.client.force_authenticate(
            user=self.normal_user
        )

        response = self.client.delete(
            f"{self.users_url}{self.normal_user.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_superuser_can_delete_staff_user(self):
        self.client.force_authenticate(
            user=self.superuser
        )

        response = self.client.delete(
            f"{self.users_url}{self.staff_user.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            User.objects.filter(
                id=self.staff_user.id
            ).exists()
        )
    def test_staff_cannot_modify_another_staff(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.patch(
            f"{self.users_url}{self.other_staff.id}/",
            {
                "first_name": "Hacked",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.other_staff.refresh_from_db()

        self.assertNotEqual(
            self.other_staff.first_name,
            "Hacked",
        )

    def test_superuser_can_modify_staff_user(self):
        self.client.force_authenticate(
            user=self.superuser
        )

        response = self.client.patch(
            f"{self.users_url}{self.staff_user.id}/",
            {
                "first_name": "UpdatedByAdmin",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.staff_user.refresh_from_db()

        self.assertEqual(
            self.staff_user.first_name,
            "UpdatedByAdmin",
        )

    def test_superuser_cannot_demote_self(self):
        self.client.force_authenticate(
            user=self.superuser
        )

        response = self.client.patch(
            f"{self.users_url}{self.superuser.id}/",
            {
                "is_superuser": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.superuser.refresh_from_db()

        self.assertTrue(
            self.superuser.is_superuser
        )

    def test_superuser_cannot_remove_own_staff_status(self):
        self.client.force_authenticate(
            user=self.superuser
        )

        response = self.client.patch(
            f"{self.users_url}{self.superuser.id}/",
            {
                "is_staff": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.superuser.refresh_from_db()

        self.assertTrue(
            self.superuser.is_staff
        )

    def test_superuser_cannot_deactivate_self(self):
        self.client.force_authenticate(
            user=self.superuser
        )

        response = self.client.patch(
            f"{self.users_url}{self.superuser.id}/",
            {
                "is_active": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.superuser.refresh_from_db()

        self.assertTrue(
            self.superuser.is_active
        )

    def test_superuser_cannot_delete_self(self):
        self.client.force_authenticate(
            user=self.superuser
        )

        response = self.client.delete(
            f"{self.users_url}{self.superuser.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            User.objects.filter(
                id=self.superuser.id
            ).exists()
        )

    def test_superuser_can_manage_other_superuser(self):
        other_superuser = User.objects.create_superuser(
            username="other_admin",
            password="StrongPassword123",
        )

        self.client.force_authenticate(
            user=self.superuser
        )

        response = self.client.patch(
            f"{self.users_url}{other_superuser.id}/",
            {
                "first_name": "UpdatedAdmin",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        other_superuser.refresh_from_db()

        self.assertEqual(
            other_superuser.first_name,
            "UpdatedAdmin",
        )

    def test_staff_can_modify_normal_user(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.patch(
            f"{self.users_url}{self.normal_user.id}/",
            {
                "first_name": "UpdatedByStaff",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.normal_user.refresh_from_db()

        self.assertEqual(
            self.normal_user.first_name,
            "UpdatedByStaff",
        )

class UserAuditAPITest(APITestCase):

    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff",
            password="StrongPassword123",
            is_staff=True,
        )

        self.normal_user = User.objects.create_user(
            username="reza",
            password="StrongPassword123",
            first_name="Reza",
            last_name="Test",
            email="reza@example.com",
        )

        self.superuser = User.objects.create_superuser(
            username="admin",
            password="StrongPassword123",
        )

        self.users_url = "/api/accounts/"
        self.audit_url = "/api/accounts/users/"

    def test_create_user_creates_audit_log(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.post(
            self.audit_url,
            {
                "username": "newuser",
                "password": "NewStrongPassword123",
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(
            username="newuser"
        )

        audit = AuditLog.objects.get(
            object_id=str(user.id)
        )

        self.assertEqual(
            audit.action,
            AuditLog.Action.CREATE,
        )

        self.assertEqual(
            audit.actor,
            self.staff_user,
        )

        self.assertEqual(
            audit.app_label,
            "accounts",
        )

        self.assertEqual(
            audit.model_name,
            "user",
        )

    def test_create_user_does_not_log_password(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.post(
            self.audit_url,
            {
                "username": "secure_user",
                "password": "SecretPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = User.objects.get(
            username="secure_user"
        )

        audit = AuditLog.objects.get(
            object_id=str(user.id)
        )

        self.assertNotIn(
            "password",
            audit.changes,
        )

        self.assertNotIn(
            "SecretPassword123",
            str(audit.changes),
        )

    def test_update_user_creates_audit_log(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.patch(
            f"{self.audit_url}{self.normal_user.id}/",
            {
                "first_name": "Updated",
                "last_name": "Person",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        audit = AuditLog.objects.filter(
            actor=self.staff_user,
            action=AuditLog.Action.UPDATE,
            object_id=str(self.normal_user.id),
        ).latest("created_at")

        self.assertEqual(
            audit.changes["first_name"]["old"],
            "Reza",
        )

        self.assertEqual(
            audit.changes["first_name"]["new"],
            "Updated",
        )

        self.assertEqual(
            audit.changes["last_name"]["old"],
            "Test",
        )

        self.assertEqual(
            audit.changes["last_name"]["new"],
            "Person",
        )

    def test_update_without_changes_does_not_create_audit_log(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        before_count = AuditLog.objects.count()

        response = self.client.patch(
            f"{self.audit_url}{self.normal_user.id}/",
            {
                "first_name": "Reza",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            AuditLog.objects.count(),
            before_count,
        )

    def test_delete_user_creates_audit_log(self):
        self.client.force_authenticate(
            user=self.superuser
        )

        user_id = self.normal_user.id

        response = self.client.delete(
            f"{self.audit_url}{user_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        audit = AuditLog.objects.get(
            object_id=str(user_id)
        )

        self.assertEqual(
            audit.action,
            AuditLog.Action.DELETE,
        )

        self.assertEqual(
            audit.actor,
            self.superuser,
        )

        self.assertEqual(
            audit.object_id,
            str(user_id),
        )

        self.assertFalse(
            User.objects.filter(
                id=user_id
            ).exists()
        )

    def test_password_change_creates_audit_log(self):
        self.client.force_authenticate(
            user=self.normal_user
        )

        response = self.client.post(
            f"{self.audit_url}{self.normal_user.id}/password/",
            {
                "new_password": "NewPassword123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        audit = AuditLog.objects.filter(
            actor=self.normal_user,
            action=AuditLog.Action.PASSWORD_CHANGE,
            object_id=str(self.normal_user.id),
        ).latest("created_at")

        self.assertEqual(
            audit.action,
            AuditLog.Action.PASSWORD_CHANGE,
        )

        self.assertEqual(
            audit.actor,
            self.normal_user,
        )

        self.assertEqual(
            audit.object_id,
            str(self.normal_user.id),
        )


    def test_password_change_does_not_store_password(self):
        self.client.force_authenticate(
            user=self.normal_user
        )

        new_password = "SuperSecretPassword123"

        response = self.client.post(
            f"{self.audit_url}{self.normal_user.id}/password/",
            {
                "new_password": new_password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        audit = AuditLog.objects.filter(
            actor=self.normal_user,
            action=AuditLog.Action.PASSWORD_CHANGE,
            object_id=str(self.normal_user.id),
        ).latest("created_at")

        self.assertNotIn(
            "password",
            audit.changes,
        )

        self.assertNotIn(
            new_password,
            str(audit.changes),
        )
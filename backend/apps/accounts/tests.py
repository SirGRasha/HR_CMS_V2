from django.test import TestCase

from apps.accounts.models import User

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
            status.HTTP_200_OK,
        )

        self.superuser.refresh_from_db()

        self.assertEqual(
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
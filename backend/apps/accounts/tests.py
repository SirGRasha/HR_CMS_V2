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
            status.HTTP_403_FORBIDDEN,
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
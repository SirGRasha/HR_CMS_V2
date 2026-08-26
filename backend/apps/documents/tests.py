from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User

from .models import Document


class DocumentAPITest(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="document_user",
            password="StrongPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="other_document_user",
            password="StrongPassword123!",
        )

        self.staff = User.objects.create_user(
            username="document_staff",
            password="StrongPassword123!",
            is_staff=True,
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.document_url = reverse(
            "document-list"
        )

    def create_file(
        self,
        name="test.pdf",
        content=b"test document",
    ):

        return SimpleUploadedFile(
            name,
            content,
            content_type="application/pdf",
        )

    def test_list_documents_requires_authentication(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            self.document_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_create_document(self):

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "مدرک پرسنلی",
                "description": "مدرک تست",
                "file": self.create_file(),
                "is_verified": False,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        document = Document.objects.get()

        self.assertEqual(
            document.title,
            "مدرک پرسنلی",
        )

        self.assertEqual(
            document.uploaded_by,
            self.user,
        )

    def test_expired_document_filter(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.CONTRACT,
            title="قرارداد منقضی",
            file=self.create_file(),
            expiry_date=(
                timezone.localdate()
                - timedelta(days=1)
            ),
            uploaded_by=self.user,
        )

        response = self.client.get(
            self.document_url,
            {
                "expiry_status": "expired"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["id"],
            document.id,
        )

    def test_no_expiry_filter(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.OTHER,
            title="سند بدون انقضا",
            file=self.create_file(),
            uploaded_by=self.user,
        )

        response = self.client.get(
            self.document_url,
            {
                "expiry_status": "no_expiry"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["id"],
            document.id,
        )

    def test_verified_filter(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.ADMINISTRATIVE,
            title="سند تایید شده",
            file=self.create_file(),
            is_verified=True,
            uploaded_by=self.user,
        )

        response = self.client.get(
            self.document_url,
            {
                "is_verified": "true"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["id"],
            document.id,
        )

    def test_document_type_filter(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.CONTRACT,
            title="قرارداد",
            file=self.create_file(),
            uploaded_by=self.user,
        )

        response = self.client.get(
            self.document_url,
            {
                "document_type": "contract"
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["id"],
            document.id,
        )

    def test_document_expiry_status_no_expiry(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.OTHER,
            title="سند",
            file=self.create_file(),
            uploaded_by=self.user,
        )

        response = self.client.get(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["expiry_status"],
            "no_expiry",
        )

    def test_document_expiry_status_expired(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.OTHER,
            title="سند منقضی",
            file=self.create_file(),
            expiry_date=(
                timezone.localdate()
                - timedelta(days=1)
            ),
            uploaded_by=self.user,
        )

        response = self.client.get(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["expiry_status"],
            "expired",
        )

    def test_document_expiry_status_valid(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.OTHER,
            title="سند معتبر",
            file=self.create_file(),
            expiry_date=(
                timezone.localdate()
                + timedelta(days=30)
            ),
            uploaded_by=self.user,
        )

        response = self.client.get(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["expiry_status"],
            "valid",
        )

    def test_document_file_exactly_10mb_is_allowed(self):

        content = b"x" * (10 * 1024 * 1024)

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "فایل 10 مگابایتی",
                "description": "تست حجم دقیق 10MB",
                "file": self.create_file(
                    name="exact_10mb.pdf",
                    content=content,
                ),
                "is_verified": False,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_document_file_over_10mb_is_rejected(self):

        content = b"x" * (10 * 1024 * 1024 + 1)

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "فایل بزرگ",
                "description": "تست فایل بزرگتر از 10MB",
                "file": self.create_file(
                    name="over_10mb.pdf",
                    content=content,
                ),
                "is_verified": False,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "file",
            response.data,
        ) 

    def test_document_file_invalid_extension_is_rejected(self):

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "فرمت غیرمجاز",
                "description": "تست فرمت فایل غیرمجاز",
                "file": self.create_file(
                    name="malicious.exe",
                    content=b"fake executable content",
                ),
                "is_verified": False,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "file",
            response.data,
        )

    def test_create_document_with_expired_date_is_rejected(self):

        expired_date = (
            timezone.localdate()
            - timedelta(days=1)
        )

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "سند با تاریخ منقضی",
                "description": "تست تاریخ انقضای گذشته",
                "file": self.create_file(),
                "expiry_date": expired_date.isoformat(),
                "is_verified": False,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "expiry_date",
            response.data,
        )

        self.assertEqual(
            Document.objects.count(),
            0,
        )

    def test_update_document_with_expired_date_is_rejected(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="سند معتبر",
            file=self.create_file(),
            expiry_date=(
                timezone.localdate()
                + timedelta(days=30)
            ),
            uploaded_by=self.user,
        )

        expired_date = (
            timezone.localdate()
            - timedelta(days=1)
        )

        response = self.client.patch(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            ),
            {
                "expiry_date": expired_date.isoformat(),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "expiry_date",
            response.data,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.expiry_date,
            timezone.localdate() + timedelta(days=30),
        )

    def test_retrieve_document(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="سند برای دریافت",
            description="تست Retrieve",
            file=self.create_file(),
            uploaded_by=self.user,
        )

        response = self.client.get(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            document.id,
        )

        self.assertEqual(
            response.data["title"],
            document.title,
        )

        self.assertEqual(
            response.data["uploaded_by"],
            self.user.id,
        )

    def test_update_document(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="عنوان اولیه",
            description="توضیح اولیه",
            file=self.create_file(),
            uploaded_by=self.user,
        )

        response = self.client.patch(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            ),
            {
                "title": "عنوان جدید",
                "description": "توضیح جدید",
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.title,
            "عنوان جدید",
        )

        self.assertEqual(
            document.description,
            "توضیح جدید",
        )

        self.assertEqual(
            document.uploaded_by,
            self.user,
        )

    def test_combined_filters(self):

        matching_document = Document.objects.create(
            document_type=Document.DocumentType.CONTRACT,
            title="سند منطبق",
            file=self.create_file(
                name="matching.pdf",
            ),
            is_verified=True,
            expiry_date=(
                timezone.localdate()
                + timedelta(days=30)
            ),
            uploaded_by=self.user,
        )

        Document.objects.create(
            document_type=Document.DocumentType.CONTRACT,
            title="نوع درست ولی تایید نشده",
            file=self.create_file(
                name="not_verified.pdf",
            ),
            is_verified=False,
            expiry_date=(
                timezone.localdate()
                + timedelta(days=30)
            ),
            uploaded_by=self.user,
        )

        Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="نوع متفاوت",
            file=self.create_file(
                name="different_type.pdf",
            ),
            is_verified=True,
            expiry_date=(
                timezone.localdate()
                + timedelta(days=30)
            ),
            uploaded_by=self.user,
        )

        response = self.client.get(
            self.document_url,
            {
                "document_type": "contract",
                "is_verified": "true",
                "expiry_status": "valid",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["id"],
            matching_document.id,
        )

    def test_invalid_is_verified_filter_is_rejected(self):

        response = self.client.get(
            self.document_url,
            {
                "is_verified": "invalid",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_expiry_status_filter_is_rejected(self):

        response = self.client.get(
            self.document_url,
            {
                "expiry_status": "invalid",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_delete_document(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.OTHER,
            title="سند قابل حذف",
            file=self.create_file(),
            uploaded_by=self.user,
        )

        response = self.client.delete(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Document.objects.filter(
                pk=document.pk
            ).exists()
        )

    def test_user_cannot_list_other_users_documents(self):

        Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Other User Document",
            file=self.create_file(
                name="other.pdf",
            ),
            uploaded_by=self.other_user,
        )

        response = self.client.get(
            self.document_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            0,
        )

    def test_user_cannot_update_other_users_document(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Private Document",
            file=self.create_file(
                name="private_update.pdf",
            ),
            uploaded_by=self.other_user,
        )

        response = self.client.patch(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            ),
            {
                "title": "Hacked Title",
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.title,
            "Private Document",
        )

    def test_staff_can_list_all_documents(self):

        Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="User Document",
            file=self.create_file(
                name="user.pdf",
            ),
            uploaded_by=self.user,
        )

        Document.objects.create(
            document_type=Document.DocumentType.CONTRACT,
            title="Other Document",
            file=self.create_file(
                name="other_staff.pdf",
            ),
            uploaded_by=self.other_user,
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.get(
            self.document_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )


    def test_staff_can_retrieve_other_users_document(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Staff Accessible Document",
            file=self.create_file(
                name="staff.pdf",
            ),
            uploaded_by=self.other_user,
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.get(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            document.id,
        )


    def test_staff_can_delete_other_users_document(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Staff Delete Document",
            file=self.create_file(
                name="staff_delete.pdf",
            ),
            uploaded_by=self.other_user,
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.delete(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Document.objects.filter(
                pk=document.pk
            ).exists()
        )

    def test_normal_user_cannot_create_verified_document(self):

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "Verified Document",
                "description": "Should not be verified by normal user.",
                "file": self.create_file(),
                "is_verified": True,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "is_verified",
            response.data,
        )

        self.assertEqual(
            Document.objects.count(),
            0,
        )

    def test_normal_user_cannot_verify_existing_document(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Unverified Document",
            file=self.create_file(),
            is_verified=False,
            uploaded_by=self.user,
        )

        response = self.client.patch(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk,
                },
            ),
            {
                "is_verified": True,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "is_verified",
            response.data,
        )

        document.refresh_from_db()

        self.assertFalse(
            document.is_verified,
        )

    def test_normal_user_cannot_unverify_verified_document(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Verified Document",
            file=self.create_file(),
            is_verified=True,
            uploaded_by=self.user,
        )

        response = self.client.patch(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk,
                },
            ),
            {
                "is_verified": False,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "is_verified",
            response.data,
        )

        document.refresh_from_db()

        self.assertTrue(
            document.is_verified,
        )

    def test_staff_can_create_verified_document(self):

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "Staff Verified Document",
                "description": "Verified by staff.",
                "file": self.create_file(),
                "is_verified": True,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        document = Document.objects.get()

        self.assertTrue(
            document.is_verified,
        )

        self.assertEqual(
            document.uploaded_by,
            self.staff,
        )

    def test_staff_can_verify_existing_document(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Pending Document",
            file=self.create_file(),
            is_verified=False,
            uploaded_by=self.user,
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk,
                },
            ),
            {
                "is_verified": True,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        document.refresh_from_db()

        self.assertTrue(
            document.is_verified,
        )

    def test_staff_can_unverify_document(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Verified Document",
            file=self.create_file(),
            is_verified=True,
            uploaded_by=self.user,
        )

        staff = User.objects.create_user(
            username="unverify_staff",
            password="StrongPassword123!",
            is_staff=True,
        )

        self.client.force_authenticate(
            user=staff
        )

        response = self.client.patch(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk,
                },
            ),
            {
                "is_verified": False,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        document.refresh_from_db()

        self.assertFalse(
            document.is_verified,
        )

    def test_user_cannot_retrieve_other_users_document(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Private Document",
            file=self.create_file(
                name="private.pdf",
            ),
            uploaded_by=self.other_user,
        )

        response = self.client.get(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_cannot_delete_other_users_document(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Private Document",
            file=self.create_file(
                name="private_delete.pdf",
            ),
            uploaded_by=self.other_user,
        )

        response = self.client.delete(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Document.objects.filter(
                pk=document.pk
            ).exists()
        )


    def test_staff_can_access_all_documents(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Other User Document",
            file=self.create_file(
                name="other.pdf",
            ),
            uploaded_by=self.other_user,
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.get(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk
                },
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            document.id,
        )

    def test_normal_user_cannot_forge_uploaded_by_on_create(self):

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "Forged Owner Test",
                "description": "Testing uploaded_by protection.",
                "file": self.create_file(
                    name="forged_owner.pdf",
                ),
                "is_verified": False,
                "uploaded_by": self.other_user.id,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        document = Document.objects.get()

        self.assertEqual(
            document.uploaded_by,
            self.user,
        )

        self.assertNotEqual(
            document.uploaded_by,
            self.other_user,
        )


    def test_normal_user_cannot_change_uploaded_by_on_update(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Original Owner",
            file=self.create_file(
                name="owner_protection.pdf",
            ),
            uploaded_by=self.user,
        )

        response = self.client.patch(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk,
                },
            ),
            {
                "title": "Updated Title",
                "uploaded_by": self.other_user.id,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.uploaded_by,
            self.user,
        )

        self.assertEqual(
            document.title,
            "Updated Title",
        )


    def test_staff_cannot_change_uploaded_by_on_update(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Staff Owner Protection",
            file=self.create_file(
                name="staff_owner_protection.pdf",
            ),
            uploaded_by=self.user,
        )

        self.client.force_authenticate(
            user=self.staff
        )

        response = self.client.patch(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk,
                },
            ),
            {
                "uploaded_by": self.other_user.id,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.uploaded_by,
            self.user,
        )


    def test_normal_user_cannot_change_uploaded_at(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Timestamp Protection",
            file=self.create_file(
                name="timestamp.pdf",
            ),
            uploaded_by=self.user,
        )

        original_uploaded_at = document.uploaded_at

        response = self.client.patch(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk,
                },
            ),
            {
                "uploaded_at": "2000-01-01T00:00:00Z",
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        document.refresh_from_db()

        self.assertEqual(
            document.uploaded_at,
            original_uploaded_at,
        )


    def test_normal_user_cannot_change_updated_at(self):

        document = Document.objects.create(
            document_type=Document.DocumentType.PERSONNEL,
            title="Updated Timestamp Protection",
            file=self.create_file(
                name="updated_timestamp.pdf",
            ),
            uploaded_by=self.user,
        )

        response = self.client.patch(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk,
                },
            ),
            {
                "updated_at": "2000-01-01T00:00:00Z",
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        document.refresh_from_db()

        self.assertNotEqual(
            document.updated_at.year,
            2000,
        )


    def test_expiry_date_today_is_valid(self):

        today = timezone.localdate()

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "Expires Today",
                "description": "Expiry date is today.",
                "file": self.create_file(
                    name="expires_today.pdf",
                ),
                "expiry_date": today.isoformat(),
                "is_verified": False,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        document = Document.objects.get()

        self.assertEqual(
            document.expiry_date,
            today,
        )

        detail_response = self.client.get(
            reverse(
                "document-detail",
                kwargs={
                    "pk": document.pk,
                },
            )
        )

        self.assertEqual(
            detail_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            detail_response.data["expiry_status"],
            "valid",
        )


    def test_uppercase_allowed_file_extension_is_accepted(self):

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "Uppercase Extension",
                "description": "Testing case-insensitive extension.",
                "file": self.create_file(
                    name="document.PDF",
                ),
                "is_verified": False,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )


    def test_file_without_extension_is_rejected(self):

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "No Extension",
                "description": "Testing missing extension.",
                "file": self.create_file(
                    name="document",
                ),
                "is_verified": False,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "file",
            response.data,
        )


    def test_normal_user_cannot_verify_using_string_true(self):

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "String True Verification",
                "description": "Testing verification protection.",
                "file": self.create_file(
                    name="string_true.pdf",
                ),
                "is_verified": "true",
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "is_verified",
            response.data,
        )

        self.assertEqual(
            Document.objects.count(),
            0,
        )


    def test_normal_user_cannot_verify_using_boolean_true(self):

        response = self.client.post(
            self.document_url,
            {
                "document_type": Document.DocumentType.PERSONNEL,
                "title": "Boolean True Verification",
                "description": "Testing verification protection.",
                "file": self.create_file(
                    name="boolean_true.pdf",
                ),
                "is_verified": True,
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "is_verified",
            response.data,
        )

        self.assertEqual(
            Document.objects.count(),
            0,
        )
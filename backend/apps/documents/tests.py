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
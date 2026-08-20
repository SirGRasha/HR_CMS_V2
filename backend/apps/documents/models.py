from django.conf import settings
from django.db import models


class Document(models.Model):

    class DocumentType(models.TextChoices):
        PERSONNEL = "personnel", "مدرک پرسنلی"
        ORGANIZATION = "organization", "مدرک سازمانی"
        CONTRACT = "contract", "قرارداد"
        CORRESPONDENCE = "correspondence", "مکاتبات"
        FINANCIAL = "financial", "مالی"
        ADMINISTRATIVE = "administrative", "اداری"
        OTHER = "other", "سایر"

    document_type = models.CharField(
        "نوع سند",
        max_length=30,
        choices=DocumentType.choices,
    )

    title = models.CharField(
        "عنوان سند",
        max_length=250,
    )

    description = models.TextField(
        "توضیحات",
        blank=True,
    )

    file = models.FileField(
        "فایل سند",
        upload_to="documents/%Y/%m/",
    )

    expiry_date = models.DateField(
        "تاریخ انقضا",
        null=True,
        blank=True,
    )

    is_verified = models.BooleanField(
        "تأیید شده",
        default=False,
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
        verbose_name="بارگذاری کننده",
    )

    uploaded_at = models.DateTimeField(
        "تاریخ بارگذاری",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخرین بروزرسانی",
        auto_now=True,
    )

    class Meta:
        verbose_name = "سند"
        verbose_name_plural = "اسناد"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title
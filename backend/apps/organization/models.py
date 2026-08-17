from django.db import models


class OrganizationUnit(models.Model):

    class UnitType(models.TextChoices):
        COMPANY = "company", "شرکت"
        MANAGEMENT = "management", "مدیریت"
        DEPUTY = "deputy", "معاونت"
        DEPARTMENT = "department", "دپارتمان"
        UNIT = "unit", "واحد"
        SECTION = "section", "بخش"

    code = models.CharField(
        "کد واحد",
        max_length=50,
        unique=True,
    )

    name = models.CharField(
        "نام واحد",
        max_length=150,
    )

    unit_type = models.CharField(
        "نوع واحد",
        max_length=20,
        choices=UnitType.choices,
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="children",
        null=True,
        blank=True,
        verbose_name="واحد والد",
    )

    is_active = models.BooleanField(
        "فعال",
        default=True,
    )

    description = models.TextField(
        "توضیحات",
        blank=True,
    )

    created_at = models.DateTimeField(
        "تاریخ ایجاد",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخرین بروزرسانی",
        auto_now=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "واحد سازمانی"
        verbose_name_plural = "واحدهای سازمانی"

    def __str__(self):
        return f"{self.code} - {self.name}"


class Position(models.Model):

    code = models.CharField(
        "کد پست",
        max_length=50,
        unique=True,
    )

    title = models.CharField(
        "عنوان پست",
        max_length=150,
    )

    organization_unit = models.ForeignKey(
        OrganizationUnit,
        on_delete=models.PROTECT,
        related_name="positions",
        verbose_name="واحد سازمانی",
    )

    is_active = models.BooleanField(
        "فعال",
        default=True,
    )

    description = models.TextField(
        "توضیحات",
        blank=True,
    )

    created_at = models.DateTimeField(
        "تاریخ ایجاد",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخرین بروزرسانی",
        auto_now=True,
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "پست سازمانی"
        verbose_name_plural = "پست‌های سازمانی"

    def __str__(self):
        return f"{self.code} - {self.title}"
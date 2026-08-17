from django.core.validators import RegexValidator
from django.db import models


class Employee(models.Model):

    class Gender(models.TextChoices):
        MALE = "male", "مرد"
        FEMALE = "female", "زن"

    class EmployeeGroup(models.TextChoices):
        ADMINISTRATIVE = "administrative", "اداری"
        PRODUCTION = "production", "تولید"

    class MilitaryStatus(models.TextChoices):
        SUBJECT = "subject", "مشمول"
        EXEMPTION = "exemption", "معافیت"
        COMPLETED = "completed", "پایان خدمت"
        SERVING = "serving", "در حال خدمت"
        EDUCATIONAL_EXEMPTION = "educational_exemption", "معافیت تحصیلی"

    class MaritalStatus(models.TextChoices):
        SINGLE = "single", "مجرد"
        MARRIED = "married", "متأهل"
        SEPARATED = "separated", "متارکه"
        WIDOWED = "widowed", "بیوه"

    class TransportationStatus(models.TextChoices):
        PERSONAL = "personal", "شخصی"
        SERVICE = "service", "سرویس"

    national_id_validator = RegexValidator(
        regex=r"^\d{10}$",
        message="کد ملی باید دقیقاً ۱۰ رقم باشد.",
    )

    personnel_code = models.CharField(
        "کد پرسنلی",
        max_length=50,
        unique=True,
    )

    first_name = models.CharField(
        "نام",
        max_length=100,
    )

    last_name = models.CharField(
        "نام خانوادگی",
        max_length=100,
    )

    gender = models.CharField(
        "جنسیت",
        max_length=10,
        choices=Gender.choices,
    )

    employee_group = models.CharField(
        "گروه",
        max_length=20,
        choices=EmployeeGroup.choices,
    )

    department = models.CharField(
        "بخش / دپارتمان",
        max_length=150,
        blank=True,
    )

    job_title = models.CharField(
        "عنوان شغلی",
        max_length=150,
        blank=True,
    )

    position = models.ForeignKey(
    "organization.Position",
    on_delete=models.PROTECT,
    related_name="employees",
    verbose_name="پست سازمانی",
    null=True,
    blank=True,
    )

    start_date = models.DateField(
        "تاریخ شروع به کار",
        null=True,
        blank=True,
    )

    insurance_date = models.DateField(
        "تاریخ بیمه شدن",
        null=True,
        blank=True,
    )

    insurance_number = models.CharField(
        "شماره بیمه",
        max_length=50,
        blank=True,
    )

    birth_date = models.DateField(
        "تاریخ تولد",
        null=True,
        blank=True,
    )

    national_id = models.CharField(
        "کد ملی",
        max_length=10,
        unique=True,
        validators=[national_id_validator],
    )

    birth_certificate_number = models.CharField(
        "شماره شناسنامه",
        max_length=50,
        blank=True,
    )

    father_name = models.CharField(
        "نام پدر",
        max_length=100,
        blank=True,
    )

    education_level = models.CharField(
        "آخرین مدرک تحصیلی",
        max_length=100,
        blank=True,
    )

    field_of_study = models.CharField(
        "رشته تحصیلی",
        max_length=150,
        blank=True,
    )

    student_number = models.CharField(
        "شماره دانشجویی",
        max_length=100,
        blank=True,
    )

    military_status = models.CharField(
        "وضعیت نظام وظیفه",
        max_length=30,
        choices=MilitaryStatus.choices,
        blank=True,
    )

    marital_status = models.CharField(
        "وضعیت تأهل",
        max_length=20,
        choices=MaritalStatus.choices,
    )

    child_count = models.PositiveSmallIntegerField(
        "تعداد فرزند",
        default=0,
    )

    landline_phone = models.CharField(
        "تلفن ثابت",
        max_length=30,
        blank=True,
    )

    residence_area = models.CharField(
        "منطقه سکونت",
        max_length=100,
        blank=True,
    )

    address = models.TextField(
        "آدرس",
        blank=True,
    )

    transportation_status = models.CharField(
        "وضعیت تردد",
        max_length=20,
        choices=TransportationStatus.choices,
        blank=True,
    )

    transportation_description = models.TextField(
        "توضیحات سرویس",
        blank=True,
    )

    contract_title = models.CharField(
        "عنوان قرارداد",
        max_length=150,
        blank=True,
    )

    contract_position = models.CharField(
        "سمت درج شده در قرارداد",
        max_length=150,
        blank=True,
    )

    notes = models.TextField(
        "توضیحات",
        blank=True,
    )

    is_active = models.BooleanField(
        "پرسنل فعال",
        default=True,
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
        verbose_name = "پرسنل"
        verbose_name_plural = "پرسنل"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.personnel_code}"

class EmployeePhone(models.Model):

    class PhoneType(models.TextChoices):
        MOBILE = "mobile", "موبایل"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="phones",
        verbose_name="پرسنل",
    )

    phone_type = models.CharField(
        "نوع تلفن",
        max_length=20,
        choices=PhoneType.choices,
        default=PhoneType.MOBILE,
    )

    phone_number = models.CharField(
        "شماره تلفن",
        max_length=20,
    )

    is_primary = models.BooleanField(
        "شماره اصلی",
        default=False,
    )
    def save(self, *args, **kwargs):
        if self.is_primary:
            EmployeePhone.objects.filter(
                employee=self.employee,
                is_primary=True,
            ).exclude(
                pk=self.pk,
            ).update(
                is_primary=False,
            )

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "تلفن پرسنل"
        verbose_name_plural = "تلفن‌های پرسنل"

    def __str__(self):
        return f"{self.employee} - {self.phone_number}"


class EmployeeChild(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name="پرسنل",
    )

    name = models.CharField(
        "نام فرزند",
        max_length=100,
    )

    birth_date = models.DateField(
        "تاریخ تولد",
    )

    education_certificate = models.BooleanField(
        "گواهی اشتغال به تحصیل",
        default=False,
    )

    is_active = models.BooleanField(
        "فعال",
        default=True,
    )

    class Meta:
        verbose_name = "فرزند"
        verbose_name_plural = "فرزندان"
        ordering = ["birth_date"]

    def __str__(self):
        return f"{self.name} - {self.employee}"

    @property
    def age(self):
        from datetime import date

        today = date.today()

        age = today.year - self.birth_date.year

        if (today.month, today.day) < (
            self.birth_date.month,
            self.birth_date.day,
        ):
            age -= 1

        return age

    @property
    def eligible_for_child_allowance(self):
        return self.age < 18 or (
            self.age >= 18 and self.education_certificate
        )


class EmployeeBankAccount(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="bank_accounts",
        verbose_name="پرسنل",
    )

    account_number = models.CharField(
        "شماره حساب",
        max_length=50,
        blank=True,
    )

    card_number = models.CharField(
        "شماره کارت",
        max_length=30,
        blank=True,
    )

    iban = models.CharField(
        "شماره شبا",
        max_length=34,
        blank=True,
    )

    bank_name = models.CharField(
        "نام بانک",
        max_length=100,
        blank=True,
    )

    is_primary = models.BooleanField(
        "حساب اصلی",
        default=False,
    )

    class Meta:
        verbose_name = "حساب بانکی"
        verbose_name_plural = "حساب‌های بانکی"

        constraints = [
            models.UniqueConstraint(
                fields=["employee"],
                condition=models.Q(is_primary=True),
                name="unique_primary_bank_account_per_employee",
            ),
        ]
    def __str__(self):
        return f"{self.employee} - {self.bank_name}"


class EmployeePromissoryNote(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="promissory_notes",
        verbose_name="پرسنل",
    )

    note_number = models.CharField(
        "شماره سفته",
        max_length=100,
    )

    class Meta:
        verbose_name = "سفته"
        verbose_name_plural = "سفته‌ها"

        constraints = [
            models.UniqueConstraint(
                fields=["employee", "note_number"],
                name="unique_promissory_note_per_employee",
            ),
        ]

    def __str__(self):
        return f"{self.employee} - {self.note_number}"

class EmployeeDocument(models.Model):

    class DocumentType(models.TextChoices):
        NATIONAL_ID = "national_id", "کارت ملی"
        BIRTH_CERTIFICATE = "birth_certificate", "شناسنامه"
        MILITARY_CARD = "military_card", "کارت پایان خدمت / معافیت"
        EDUCATION = "education", "مدرک تحصیلی"
        INSURANCE = "insurance", "مدرک بیمه"
        NO_CRIMINAL_RECORD = "no_criminal_record", "عدم سوءپیشینه"
        NO_ADDICTION = "no_addiction", "عدم اعتیاد"
        OCCUPATIONAL_HEALTH = "occupational_health", "طب کار"
        CONTRACT = "contract", "قرارداد"
        OTHER = "other", "سایر"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="پرسنل",
    )

    document_type = models.CharField(
        "نوع مدرک",
        max_length=50,
        choices=DocumentType.choices,
    )

    title = models.CharField(
        "عنوان مدرک",
        max_length=200,
    )

    file = models.FileField(
        "فایل مدرک",
        upload_to="personnel/documents/%Y/%m/",
    )

    description = models.TextField(
        "توضیحات",
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        "تاریخ بارگذاری",
        auto_now_add=True,
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

    class Meta:
        verbose_name = "مدرک پرسنلی"
        verbose_name_plural = "مدارک پرسنلی"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.employee} - {self.title}"


class EmployeeEvaluation(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="evaluations",
        verbose_name="پرسنل",
    )

    score = models.DecimalField(
        "نمره ارزیابی",
        max_digits=5,
        decimal_places=2,
    )

    evaluation_date = models.DateField(
        "تاریخ ارزیابی",
    )

    description = models.TextField(
        "توضیحات",
        blank=True,
    )

    created_at = models.DateTimeField(
        "تاریخ ثبت",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "ارزیابی پرسنل"
        verbose_name_plural = "ارزیابی‌های پرسنل"
        ordering = ["-evaluation_date"]

    def __str__(self):
        return (
            f"{self.employee} - "
            f"{self.score} - "
            f"{self.evaluation_date}"
        )


class EmployeeContract(models.Model):

    class ContractType(models.TextChoices):
        FULL_TIME = "full_time", "تمام وقت"
        PART_TIME = "part_time", "پاره وقت"
        TEMPORARY = "temporary", "موقت"
        PROJECT = "project", "پروژه‌ای"
        OTHER = "other", "سایر"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="contracts",
        verbose_name="پرسنل",
    )

    contract_type = models.CharField(
        "نوع قرارداد",
        max_length=30,
        choices=ContractType.choices,
    )

    title = models.CharField(
        "عنوان قرارداد",
        max_length=200,
    )

    position = models.CharField(
        "سمت",
        max_length=200,
    )

    start_date = models.DateField(
        "تاریخ شروع قرارداد",
    )

    end_date = models.DateField(
        "تاریخ پایان قرارداد",
        null=True,
        blank=True,
    )

    description = models.TextField(
        "توضیحات",
        blank=True,
    )

    file = models.FileField(
        "فایل قرارداد",
        upload_to="personnel/contracts/%Y/%m/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        "قرارداد فعال",
        default=True,
    )

    created_at = models.DateTimeField(
        "تاریخ ثبت",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "قرارداد پرسنل"
        verbose_name_plural = "قراردادهای پرسنل"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.employee} - {self.title}"
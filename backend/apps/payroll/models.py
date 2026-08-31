from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class EmployeeSalary(models.Model):

    employee = models.ForeignKey(
        "personnel.Employee",
        on_delete=models.CASCADE,
        related_name="salary_records",
        verbose_name="پرسنل",
    )

    year = models.PositiveSmallIntegerField(
    "سال",
    validators=[
        MinValueValidator(1300),
    ],
    )

    month = models.PositiveSmallIntegerField(
        "ماه",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ],
    )

    monthly_wage = models.DecimalField(
        "مزد ماهیانه",
        max_digits=15,
        decimal_places=0,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    worker_food_allowance = models.DecimalField(
        "بن کارگری",
        max_digits=15,
        decimal_places=0,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    housing_allowance = models.DecimalField(
        "حق مسکن",
        max_digits=15,
        decimal_places=0,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    child_allowance = models.DecimalField(
        "حق اولاد",
        max_digits=15,
        decimal_places=0,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    marriage_allowance = models.DecimalField(
        "حق تأهل",
        max_digits=15,
        decimal_places=0,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    notes = models.TextField(
        "توضیحات",
        blank=True,
    )

    created_at = models.DateTimeField(
        "تاریخ ثبت",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخرین بروزرسانی",
        auto_now=True,
    )

    class Meta:
        verbose_name = "حقوق و مزایا"
        verbose_name_plural = "حقوق و مزایا"
        ordering = ["-year", "-month"]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "year", "month"],
                name="unique_employee_salary_period",
            )
        ]

    @property
    def total_compensable(self):
        return (
            self.monthly_wage
            + self.worker_food_allowance
            + self.housing_allowance
            + self.child_allowance
            + self.marriage_allowance
        )

    @property
    def daily_wage(self):
        return self.monthly_wage / Decimal("30")

    def __str__(self):
        return (
            f"{self.employee} - "
            f"{self.year}/{self.month}"
        )

class PayrollBonus(models.Model):
    salary = models.ForeignKey(
        EmployeeSalary,
        on_delete=models.CASCADE,
        related_name="bonuses",
        verbose_name="حقوق",
    )

    title = models.CharField(
        "عنوان پاداش",
        max_length=150,
    )

    amount = models.DecimalField(
        "مبلغ",
        max_digits=15,
        decimal_places=0,
        validators=[
            MinValueValidator(0),
        ],
        default=0,
    )

    description = models.CharField(
        "توضیحات",
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(
        "تاریخ ثبت",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخرین بروزرسانی",
        auto_now=True,
    )

    class Meta:
        verbose_name = "پاداش حقوق"
        verbose_name_plural = "پاداش‌های حقوق"
        ordering = ["id"]

    def __str__(self):
        return (
            f"{self.salary} - "
            f"{self.title} - "
            f"{self.amount}"
        )
class PayrollDeduction(models.Model):

    class DeductionType(models.TextChoices):
        INSURANCE = "insurance", "بیمه"
        TAX = "tax", "مالیات"
        ADVANCE = "advance", "مساعده"
        LOAN = "loan", "وام"
        ABSENCE = "absence", "غیبت / کسرکار"
        OTHER = "other", "سایر"

    salary = models.ForeignKey(
        EmployeeSalary,
        on_delete=models.CASCADE,
        related_name="deductions",
        verbose_name="حقوق",
    )

    deduction_type = models.CharField(
        "نوع کسور",
        max_length=30,
        choices=DeductionType.choices,
    )

    amount = models.DecimalField(
        "مبلغ",
        max_digits=15,
        decimal_places=0,
        validators=[
            MinValueValidator(0),
        ],
        default=0,
    )

    description = models.CharField(
        "توضیحات",
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(
        "تاریخ ثبت",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخرین بروزرسانی",
        auto_now=True,
    )

    class Meta:
        verbose_name = "کسور حقوق"
        verbose_name_plural = "کسورات حقوق"
        ordering = ["deduction_type", "id"]

    def __str__(self):
        return (
            f"{self.salary} - "
            f"{self.get_deduction_type_display()} - "
            f"{self.amount}"
        )
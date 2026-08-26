import os

from rest_framework import serializers

from .models import Employee
from .models import EmployeeChild
from .models import EmployeeDocument
from .models import EmployeePhone
from .models import EmployeeBankAccount
from .models import EmployeePromissoryNote
from apps.organization.models import Position
from apps.core.fields import JalaliDateField


MAX_DOCUMENT_SIZE = 10 * 1024 * 1024

ALLOWED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
}


def validate_iranian_national_id(value):
    """
    اعتبارسنجی کد ملی ایران
    """

    value = str(value).strip()

    if not value.isdigit():
        raise serializers.ValidationError(
            "کد ملی باید فقط شامل اعداد باشد."
        )

    if len(value) != 10:
        raise serializers.ValidationError(
            "کد ملی باید دقیقاً ۱۰ رقم باشد."
        )

    if len(set(value)) == 1:
        raise serializers.ValidationError(
            "کد ملی وارد شده معتبر نیست."
        )

    digits = [int(x) for x in value]

    check_digit = digits[9]

    total = sum(
        digits[i] * (10 - i)
        for i in range(9)
    )

    remainder = total % 11

    if remainder < 2:
        calculated_digit = remainder
    else:
        calculated_digit = 11 - remainder

    if calculated_digit != check_digit:
        raise serializers.ValidationError(
            "کد ملی وارد شده معتبر نیست."
        )

    return value

def validate_iranian_mobile_number(value):
    value = str(value).strip()

    if not value.isdigit():
        raise serializers.ValidationError(
            "شماره موبایل باید فقط شامل اعداد باشد."
        )

    if len(value) != 11:
        raise serializers.ValidationError(
            "شماره موبایل باید دقیقاً ۱۱ رقم باشد."
        )

    if not value.startswith("09"):
        raise serializers.ValidationError(
            "شماره موبایل باید با 09 شروع شود."
        )

    return value

class EmployeePhoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeePhone
        fields = "__all__"

    def validate_phone_number(self, value):
        return validate_iranian_mobile_number(value)

class EmployeeBankAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeBankAccount
        fields = "__all__"

    def validate(self, attrs):
        employee = attrs.get("employee")
        is_primary = attrs.get("is_primary", False)

        if employee and is_primary:
            queryset = EmployeeBankAccount.objects.filter(
                employee=employee,
                is_primary=True,
            )

            if self.instance:
                queryset = queryset.exclude(
                    pk=self.instance.pk
                )

            if queryset.exists():
                raise serializers.ValidationError({
                    "is_primary": (
                        "این پرسنل قبلاً یک حساب بانکی اصلی دارد."
                    )
                })

        return attrs

    def validate_card_number(self, value):
        value = str(value).strip()

        if value and not value.isdigit():
            raise serializers.ValidationError(
                "شماره کارت باید فقط شامل اعداد باشد."
            )

        if value and len(value) != 16:
            raise serializers.ValidationError(
                "شماره کارت باید دقیقاً ۱۶ رقم باشد."
            )

        return value

    def validate_iban(self, value):
        value = str(value).strip().upper()

        if value:
            if not value.startswith("IR"):
                raise serializers.ValidationError(
                    "شماره شبا باید با IR شروع شود."
                )

            if len(value) != 26:
                raise serializers.ValidationError(
                    "شماره شبا باید دقیقاً ۲۶ کاراکتر باشد."
                )

        return value

class EmployeePromissoryNoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeePromissoryNote
        fields = "__all__"

    def validate_note_number(self, value):
        value = str(value).strip()

        if not value:
            raise serializers.ValidationError(
                "شماره سفته نمی‌تواند خالی باشد."
            )

        return value

class EmployeeSerializer(serializers.ModelSerializer):

    position_detail = serializers.SerializerMethodField()

    birth_date = JalaliDateField(
        allow_null=True,
        required=False,
    )

    start_date = JalaliDateField(
        allow_null=True,
        required=False,
    )

    insurance_date = JalaliDateField(
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "user",
            "personnel_code",
            "first_name",
            "last_name",
            "gender",
            "employee_group",
            "department",
            "job_title",
            "position",
            "position_detail",
            "start_date",
            "insurance_date",
            "insurance_number",
            "birth_date",
            "national_id",
            "birth_certificate_number",
            "father_name",
            "education_level",
            "field_of_study",
            "student_number",
            "military_status",
            "marital_status",
            "child_count",
            "landline_phone",
            "residence_area",
            "address",
            "transportation_status",
            "transportation_description",
            "contract_title",
            "contract_position",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "position_detail",
        ]

    def get_position_detail(self, obj):
        if not obj.position:
            return None

        position = obj.position

        return {
            "id": position.id,
            "code": position.code,
            "title": position.title,
            "is_active": position.is_active,
            "organization_unit": {
                "id": position.organization_unit.id,
                "code": position.organization_unit.code,
                "name": position.organization_unit.name,
            },
        }

    def validate_national_id(self, value):
        return validate_iranian_national_id(value)

    def validate(self, attrs):
        from django.utils import timezone

        today = timezone.localdate()

        birth_date = attrs.get(
            "birth_date",
            getattr(self.instance, "birth_date", None),
        )

        start_date = attrs.get(
            "start_date",
            getattr(self.instance, "start_date", None),
        )

        insurance_date = attrs.get(
            "insurance_date",
            getattr(self.instance, "insurance_date", None),
        )

        if birth_date and birth_date > today:
            raise serializers.ValidationError({
                "birth_date":
                    "تاریخ تولد نمی‌تواند در آینده باشد."
            })

        if start_date and start_date > today:
            raise serializers.ValidationError({
                "start_date":
                    "تاریخ شروع به کار نمی‌تواند در آینده باشد."
            })

        if birth_date and start_date and start_date < birth_date:
            raise serializers.ValidationError({
                "start_date":
                    "تاریخ شروع به کار نمی‌تواند قبل از تاریخ تولد باشد."
            })

        if (
            insurance_date
            and start_date
            and insurance_date < start_date
        ):
            raise serializers.ValidationError({
                "insurance_date":
                    "تاریخ بیمه نمی‌تواند قبل از تاریخ شروع به کار باشد."
            })

        position = attrs.get(
            "position",
            getattr(self.instance, "position", None),
        )

        if position and not position.is_active:
            raise serializers.ValidationError({
                "position":
                    "امکان اختصاص سمت غیرفعال به پرسنل وجود ندارد."
            })

        return attrs


class EmployeeChildSerializer(serializers.ModelSerializer):

    birth_date = JalaliDateField()

    class Meta:
        model = EmployeeChild
        fields = "__all__"

class EmployeeDocumentSerializer(serializers.ModelSerializer):

    expiry_date = JalaliDateField(
    required=False,
    allow_null=True,
    )

    expiry_status = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeDocument
        fields = "__all__"
        read_only_fields = (
            "id",
            "uploaded_at",
            "expiry_status",
        )

    def get_expiry_status(self, obj):
        from django.utils import timezone

        if obj.expiry_date is None:
            return "no_expiry"

        if obj.expiry_date < timezone.localdate():
            return "expired"

        return "valid"

    def validate_file(self, value):
        """
        اعتبارسنجی فایل سند پرسنلی
        """

        if value.size > MAX_DOCUMENT_SIZE:
            raise serializers.ValidationError(
                "حجم فایل نباید بیشتر از ۱۰ مگابایت باشد."
            )

        extension = os.path.splitext(value.name)[1].lower()

        if extension not in ALLOWED_DOCUMENT_EXTENSIONS:
            raise serializers.ValidationError(
                "فرمت فایل مجاز نیست. فقط PDF، JPG، JPEG و PNG مجاز هستند."
            )

        return value
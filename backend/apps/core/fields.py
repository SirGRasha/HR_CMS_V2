from datetime import date

from rest_framework import serializers

from .jalali import (
    gregorian_to_jalali,
    jalali_to_gregorian,
)


class JalaliDateField(serializers.DateField):
    """
    DRF DateField with Jalali date input/output.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("allow_null", True)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if data is None:
            return None

        if data == "":
            raise serializers.ValidationError(
                "تاریخ شمسی نمی‌تواند خالی باشد. "
                "فرمت صحیح: YYYY-MM-DD"
            )

        if not isinstance(data, str):
            raise serializers.ValidationError(
                "تاریخ باید به صورت رشته وارد شود."
            )

        try:
            gregorian_date = jalali_to_gregorian(
                data.strip()
            )
        except (TypeError, ValueError):
            raise serializers.ValidationError(
                "تاریخ شمسی نامعتبر است. "
                "فرمت صحیح: YYYY-MM-DD"
            )

        return gregorian_date

    def to_representation(self, value):
        if value is None:
            return None

        if isinstance(value, str):
            try:
                value = date.fromisoformat(value)
            except ValueError:
                return value

        return gregorian_to_jalali(value)
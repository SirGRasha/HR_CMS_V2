from datetime import date, datetime

from django.test import SimpleTestCase

from .jalali import (
    gregorian_to_jalali,
    jalali_to_gregorian,
    today_jalali,
)
from rest_framework.serializers import ValidationError

from .fields import JalaliDateField


class JalaliConversionTests(SimpleTestCase):

    def test_gregorian_to_jalali(self):
        result = gregorian_to_jalali(
            date(2026, 8, 26)
        )

        self.assertEqual(
            result,
            "1405-06-04",
        )

    def test_jalali_to_gregorian(self):
        result = jalali_to_gregorian(
            "1405-06-04"
        )

        self.assertEqual(
            result,
            date(2026, 8, 26),
        )

    def test_datetime_to_jalali(self):
        result = gregorian_to_jalali(
            datetime(2026, 8, 26, 15, 30, 45)
        )

        self.assertEqual(
            result,
            "1405-06-04",
        )

    def test_none_to_jalali(self):
        self.assertIsNone(
            gregorian_to_jalali(None)
        )

    def test_none_to_gregorian(self):
        self.assertIsNone(
            jalali_to_gregorian(None)
        )

    def test_invalid_gregorian_type(self):
        with self.assertRaises(TypeError):
            gregorian_to_jalali(
                "2026-08-26"
            )

    def test_invalid_jalali_type(self):
        with self.assertRaises(TypeError):
            jalali_to_gregorian(
                date(2026, 8, 26)
            )

    def test_invalid_jalali_format(self):
        with self.assertRaises(ValueError):
            jalali_to_gregorian(
                "1405/06/04"
            )

    def test_invalid_jalali_value(self):
        with self.assertRaises(ValueError):
            jalali_to_gregorian(
                "1405-13-01"
            )

    def test_today_jalali(self):
        expected = gregorian_to_jalali(
            date.today()
        )

        self.assertEqual(
            today_jalali(),
            expected,
        )

class JalaliDateFieldTests(SimpleTestCase):

    def setUp(self):
        self.field = JalaliDateField()

    def test_jalali_input_returns_gregorian_date(self):
        result = self.field.to_internal_value(
            "1405-06-04"
        )

        self.assertEqual(
            result,
            date(2026, 8, 26),
        )

    def test_gregorian_date_is_rendered_as_jalali(self):
        result = self.field.to_representation(
            date(2026, 8, 26)
        )

        self.assertEqual(
            result,
            "1405-06-04",
        )

    def test_none_input(self):
        result = self.field.run_validation(None)

        self.assertIsNone(result)

    def test_empty_input_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.field.run_validation("")

    def test_invalid_jalali_date(self):
        with self.assertRaises(ValidationError):
            self.field.to_internal_value(
                "1405-13-01"
            )

    def test_invalid_jalali_format(self):
        with self.assertRaises(ValidationError):
            self.field.to_internal_value(
                "1405/06/04"
            )

    def test_invalid_input_type(self):
        with self.assertRaises(ValidationError):
            self.field.to_internal_value(
                14050604
            )

    def test_datetime_output(self):
        result = self.field.to_representation(
            datetime(
                2026,
                8,
                26,
                15,
                30,
            )
        )

        self.assertEqual(
            result,
            "1405-06-04",
        )
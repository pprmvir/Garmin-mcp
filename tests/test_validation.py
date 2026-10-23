import unittest

from garmin.validation import validate_date, validate_date_range


class DateValidationTests(unittest.TestCase):
    def test_validate_date_returns_iso_date(self):
        self.assertEqual(validate_date("2026-10-23", "calendar_date"), "2026-10-23")

    def test_validate_date_rejects_invalid_values(self):
        for value in ("2026-2-3", "23-10-2026", "2026-02-30", None):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "calendar_date"):
                    validate_date(value, "calendar_date")

    def test_validate_date_range_returns_dates_in_order(self):
        self.assertEqual(
            validate_date_range("2026-10-01", "2026-10-23"),
            ("2026-10-01", "2026-10-23"),
        )

    def test_validate_date_range_rejects_reverse_range(self):
        with self.assertRaisesRegex(ValueError, "start_date must be on or before"):
            validate_date_range("2026-10-23", "2026-10-01")

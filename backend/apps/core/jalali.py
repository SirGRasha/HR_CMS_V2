import jdatetime
from datetime import date, datetime


def gregorian_to_jalali(value):
    """
    Convert Gregorian date/datetime to Jalali date string.

    date     -> YYYY-MM-DD
    datetime -> YYYY-MM-DD
    None     -> None
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        value = value.date()

    if not isinstance(value, date):
        raise TypeError(
            "value must be a date, datetime, or None."
        )

    jalali = jdatetime.date.fromgregorian(
        date=value
    )

    return jalali.strftime("%Y-%m-%d")


def jalali_to_gregorian(value):
    """
    Convert Jalali date string to Gregorian date.

    Input:
        YYYY-MM-DD

    Output:
        datetime.date
    """

    if value is None:
        return None

    if isinstance(value, str):
        value = value.strip()

    if not isinstance(value, str):
        raise TypeError(
            "value must be a Jalali date string or None."
        )

    try:
        year, month, day = map(
            int,
            value.split("-"),
        )
    except (ValueError, AttributeError):
        raise ValueError(
            "Jalali date must be in YYYY-MM-DD format."
        )

    jalali = jdatetime.date(
        year,
        month,
        day,
    )

    return jalali.togregorian()


def today_jalali():
    """
    Return today's Jalali date as YYYY-MM-DD.
    """

    return jdatetime.date.today().strftime(
        "%Y-%m-%d"
    )
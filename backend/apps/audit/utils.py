from datetime import date, datetime
from decimal import Decimal


def make_json_safe(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, dict):
        return {
            key: make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [
            make_json_safe(item)
            for item in value
        ]

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def build_changes(
    old_instance,
    new_instance,
    fields,
):
    changes = {}

    for field in fields:
        old_value = getattr(
            old_instance,
            field,
            None,
        )

        new_value = getattr(
            new_instance,
            field,
            None,
        )

        if old_value != new_value:
            changes[field] = {
                "old": make_json_safe(old_value),
                "new": make_json_safe(new_value),
            }

    return changes

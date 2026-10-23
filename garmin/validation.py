from datetime import date


def validate_date(value: str, name: str) -> str:
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a date in YYYY-MM-DD format") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"{name} must be a date in YYYY-MM-DD format")
    return value


def validate_date_range(start_date: str, end_date: str) -> tuple[str, str]:
    start = validate_date(start_date, "start_date")
    end = validate_date(end_date, "end_date")
    if start > end:
        raise ValueError("start_date must be on or before end_date")
    return start, end

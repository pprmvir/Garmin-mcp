from garmin.validation import validate_date_range


async def get_recent_activities(
    client,
    limit: int = 10,
    start: int = 0,
    start_date: str | None = None,
    end_date: str | None = None,
    activity_type: str | None = None,
) -> list[dict]:
    if not 1 <= limit <= 50:
        raise ValueError("limit must be between 1 and 50")
    if start < 0:
        raise ValueError("start must be zero or greater")
    if (start_date is None) != (end_date is None):
        raise ValueError("start_date and end_date must be provided together")

    params = {"start": start, "limit": limit}
    if start_date and end_date:
        start_date, end_date = validate_date_range(start_date, end_date)
        params.update(startDate=start_date, endDate=end_date)
    if activity_type:
        params["activityType"] = activity_type

    data = await client.get_json(
        "/activitylist-service/activities/search/activities", params=params
    )
    if not isinstance(data, list):
        raise RuntimeError("Unexpected Garmin activity list response format")

    return data

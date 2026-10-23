from garmin.validation import validate_date


async def get_daily_heart_rate(client, calendar_date: str):
    calendar_date = validate_date(calendar_date, "calendar_date")
    return await client.get_json(
        "/wellness-service/wellness/dailyHeartRate",
        params={"date": calendar_date},
    )

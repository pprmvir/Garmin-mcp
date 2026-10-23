from garmin.validation import validate_date


async def get_daily_summary(client, calendar_date: str):
    calendar_date = validate_date(calendar_date, "calendar_date")
    return await client.get_json(
        "/usersummary-service/usersummary/daily",
        params={"calendarDate": calendar_date},
    )

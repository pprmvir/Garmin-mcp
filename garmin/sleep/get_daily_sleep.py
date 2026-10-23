from garmin.validation import validate_date


async def get_daily_sleep(client, calendar_date: str):
    calendar_date = validate_date(calendar_date, "calendar_date")
    return await client.get_json(
        "/sleep-service/sleep/dailySleep", params={"date": calendar_date}
    )

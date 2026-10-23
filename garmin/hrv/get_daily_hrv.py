from urllib.parse import quote

from garmin.validation import validate_date


async def get_daily_hrv(client, calendar_date: str):
    calendar_date = validate_date(calendar_date, "calendar_date")
    return await client.get_json(f"/hrv-service/hrv/{quote(calendar_date)}")

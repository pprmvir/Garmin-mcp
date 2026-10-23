from urllib.parse import quote

from garmin.validation import validate_date


async def get_daily_spo2(client, calendar_date: str):
    calendar_date = validate_date(calendar_date, "calendar_date")
    return await client.get_json(
        f"/wellness-service/wellness/daily/spo2acclimation/{quote(calendar_date)}"
    )

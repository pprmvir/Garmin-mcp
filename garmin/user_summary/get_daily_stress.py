from urllib.parse import quote

from garmin.validation import validate_date_range


async def get_daily_stress(client, start_date: str, end_date: str):
    start_date, end_date = validate_date_range(start_date, end_date)
    return await client.get_json(
        f"/usersummary-service/stats/stress/daily/{quote(start_date)}/{quote(end_date)}"
    )

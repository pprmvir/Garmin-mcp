from urllib.parse import quote

from garmin.validation import validate_date_range


async def get_wellness_activity_summaries(
    client, start_date: str, end_date: str
):
    start_date, end_date = validate_date_range(start_date, end_date)
    return await client.get_json(
        f"/wellnessactivity-service/activity/summary/range/{quote(start_date)}/{quote(end_date)}"
    )

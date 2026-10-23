from garmin.validation import validate_date_range


async def get_sleep_summaries(client, start_date: str, end_date: str):
    start_date, end_date = validate_date_range(start_date, end_date)
    return await client.get_json(
        "/sleep-service/sleep/dailySleepSummariesByDate",
        params={"startDate": start_date, "endDate": end_date},
    )

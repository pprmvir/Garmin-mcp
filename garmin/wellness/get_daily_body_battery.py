from garmin.validation import validate_date_range


async def get_daily_body_battery(client, start_date: str, end_date: str):
    start_date, end_date = validate_date_range(start_date, end_date)
    return await client.get_json(
        "/wellness-service/wellness/bodyBattery/reports/daily",
        params={"startDate": start_date, "endDate": end_date},
    )

async def get_activity_details(client, activity_id: int) -> dict:
    if activity_id <= 0:
        raise ValueError("activity_id must be a positive integer")
    data = await client.get_json(f"/activity-service/activity/{activity_id}")
    if not isinstance(data, dict):
        raise RuntimeError("Unexpected Garmin activity details response format")
    return data

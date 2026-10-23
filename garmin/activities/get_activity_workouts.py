async def get_activity_workouts(client, activity_id: int):
    if activity_id <= 0:
        raise ValueError("activity_id must be a positive integer")
    return await client.get_json(f"/activity-service/activity/{activity_id}/workouts")

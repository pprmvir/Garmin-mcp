import logging
import os

from mcp.server import MCPServer

from garmin.activities import (
    get_activity_details as fetch_activity_details,
    get_activity_workouts as fetch_activity_workouts,
    get_recent_activities as fetch_recent_activities,
)
from garmin.hrv import (
    get_daily_hrv as fetch_daily_hrv,
    get_hrv_summaries as fetch_hrv_summaries,
)
from garmin.sleep import (
    get_daily_sleep as fetch_daily_sleep,
    get_sleep_summaries as fetch_sleep_summaries,
)
from garmin.user_summary import (
    get_daily_hydration as fetch_daily_hydration,
    get_daily_steps as fetch_daily_steps,
    get_daily_stress as fetch_daily_stress,
    get_daily_summaries as fetch_daily_summaries,
    get_daily_summary as fetch_daily_summary,
)
from garmin.wellness import (
    get_daily_body_battery as fetch_daily_body_battery,
    get_daily_heart_rate as fetch_daily_heart_rate,
    get_daily_spo2 as fetch_daily_spo2,
    get_wellness_activity_summaries as fetch_wellness_activity_summaries,
)
from garmin_client import GarminClient

logging.basicConfig(level=logging.INFO)

mcp = MCPServer("Garmin Personal Fitness")
garmin = GarminClient()


@mcp.tool()
async def check_garmin_connection() -> dict:
    """Check whether Garmin Personal API authentication works.
    Does not return credentials or personal health data.
    """
    try:
        await garmin.get_access_token()
        return {
            "connected": True,
            "message": "Garmin authentication succeeded.",
        }
    except Exception:
        logging.exception("Garmin authentication failed")
        return {
            "connected": False,
            "message": (
                "Authentication failed. Check server logs "
                "and verify your Garmin API key."
            ),
        }

@mcp.tool()
async def get_recent_activities(
    limit: int = 10,
    start: int = 0,
    start_date: str | None = None,
    end_date: str | None = None,
    activity_type: str | None = None,
) -> list[dict]:
    """Retrieve Garmin activity summaries, optionally filtered by date and type."""
    return await fetch_recent_activities(
        garmin,
        limit=limit,
        start=start,
        start_date=start_date,
        end_date=end_date,
        activity_type=activity_type,
    )


@mcp.tool()
async def get_activity_details(activity_id: int) -> dict:
    """Retrieve detailed information for a Garmin activity using its activity ID."""
    return await fetch_activity_details(garmin, activity_id)


@mcp.tool()
async def get_activity_workouts(activity_id: int):
    """Retrieve workout intervals or steps associated with an activity."""
    return await fetch_activity_workouts(garmin, activity_id)


@mcp.tool()
async def get_daily_sleep(calendar_date: str):
    """Retrieve Garmin sleep data for a date in YYYY-MM-DD format."""
    return await fetch_daily_sleep(garmin, calendar_date)


@mcp.tool()
async def get_sleep_summaries(start_date: str, end_date: str):
    """Retrieve Garmin sleep summaries for an inclusive date range."""
    return await fetch_sleep_summaries(garmin, start_date, end_date)


@mcp.tool()
async def get_daily_hrv(calendar_date: str):
    """Retrieve Garmin HRV data for a date in YYYY-MM-DD format."""
    return await fetch_daily_hrv(garmin, calendar_date)


@mcp.tool()
async def get_hrv_summaries(start_date: str, end_date: str):
    """Retrieve Garmin HRV summaries for a date range."""
    return await fetch_hrv_summaries(garmin, start_date, end_date)


@mcp.tool()
async def get_daily_summary(calendar_date: str):
    """Retrieve Garmin's daily user summary for a date in YYYY-MM-DD format."""
    return await fetch_daily_summary(garmin, calendar_date)


@mcp.tool()
async def get_daily_summaries(start_date: str, end_date: str):
    """Retrieve Garmin daily summaries for a date range."""
    return await fetch_daily_summaries(garmin, start_date, end_date)


@mcp.tool()
async def get_daily_hydration(start_date: str, end_date: str):
    """Retrieve daily hydration statistics for a date range."""
    return await fetch_daily_hydration(garmin, start_date, end_date)


@mcp.tool()
async def get_daily_steps(start_date: str, end_date: str):
    """Retrieve daily step statistics for a date range."""
    return await fetch_daily_steps(garmin, start_date, end_date)


@mcp.tool()
async def get_daily_stress(start_date: str, end_date: str):
    """Retrieve daily stress statistics for a date range."""
    return await fetch_daily_stress(garmin, start_date, end_date)


@mcp.tool()
async def get_daily_body_battery(start_date: str, end_date: str):
    """Retrieve daily Body Battery reports for a date range."""
    return await fetch_daily_body_battery(garmin, start_date, end_date)


@mcp.tool()
async def get_daily_heart_rate(calendar_date: str):
    """Retrieve daily heart-rate data for a date in YYYY-MM-DD format."""
    return await fetch_daily_heart_rate(garmin, calendar_date)


@mcp.tool()
async def get_daily_spo2(calendar_date: str):
    """Retrieve daily SpO2 and acclimation data for a date."""
    return await fetch_daily_spo2(garmin, calendar_date)


@mcp.tool()
async def get_wellness_activity_summaries(start_date: str, end_date: str):
    """Retrieve daily wellness activity summaries for a date range."""
    return await fetch_wellness_activity_summaries(
        garmin, start_date, end_date
    )


print("Registered tools:", [
    tool.name for tool in mcp._tool_manager.list_tools()
])

if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )

import unittest
from unittest.mock import AsyncMock

from garmin.activities import (
    get_activity_details,
    get_activity_workouts,
    get_recent_activities,
)
from garmin.hrv import get_daily_hrv, get_hrv_summaries
from garmin.sleep import get_daily_sleep, get_sleep_summaries
from garmin.user_summary import (
    get_daily_hydration,
    get_daily_steps,
    get_daily_stress,
    get_daily_summaries,
    get_daily_summary,
)
from garmin.wellness import (
    get_daily_body_battery,
    get_daily_heart_rate,
    get_daily_spo2,
    get_wellness_activity_summaries,
)


class ServiceFunctionTests(unittest.IsolatedAsyncioTestCase):
    async def test_date_and_range_endpoints_build_expected_requests(self):
        single_date = "2026-10-23"
        start_date = "2026-10-01"
        end_date = "2026-10-23"
        cases = (
            (get_daily_sleep, (single_date,), "/sleep-service/sleep/dailySleep", {"date": single_date}),
            (get_sleep_summaries, (start_date, end_date), "/sleep-service/sleep/dailySleepSummariesByDate", {"startDate": start_date, "endDate": end_date}),
            (get_daily_hrv, (single_date,), f"/hrv-service/hrv/{single_date}", None),
            (get_hrv_summaries, (start_date, end_date), f"/hrv-service/hrv/daily/{start_date}/{end_date}", None),
            (get_daily_summary, (single_date,), "/usersummary-service/usersummary/daily", {"calendarDate": single_date}),
            (get_daily_summaries, (start_date, end_date), "/usersummary-service/v2/dailysummaries", {"startDate": start_date, "endDate": end_date}),
            (get_daily_hydration, (start_date, end_date), f"/usersummary-service/stats/hydration/daily/{start_date}/{end_date}", None),
            (get_daily_steps, (start_date, end_date), f"/usersummary-service/stats/steps/daily/{start_date}/{end_date}", None),
            (get_daily_stress, (start_date, end_date), f"/usersummary-service/stats/stress/daily/{start_date}/{end_date}", None),
            (get_daily_body_battery, (start_date, end_date), "/wellness-service/wellness/bodyBattery/reports/daily", {"startDate": start_date, "endDate": end_date}),
            (get_daily_heart_rate, (single_date,), "/wellness-service/wellness/dailyHeartRate", {"date": single_date}),
            (get_daily_spo2, (single_date,), f"/wellness-service/wellness/daily/spo2acclimation/{single_date}", None),
            (get_wellness_activity_summaries, (start_date, end_date), f"/wellnessactivity-service/activity/summary/range/{start_date}/{end_date}", None),
        )

        for function, arguments, path, params in cases:
            with self.subTest(function=function.__name__):
                client = AsyncMock()
                client.get_json.return_value = {"result": "ok"}

                result = await function(client, *arguments)

                self.assertEqual(result, {"result": "ok"})
                if params is None:
                    client.get_json.assert_awaited_once_with(path)
                else:
                    client.get_json.assert_awaited_once_with(path, params=params)

    async def test_recent_activities_filters_response_and_passes_filters(self):
        client = AsyncMock()
        client.get_json.return_value = [
            {
                "activityId": 123,
                "activityName": "Morning Run",
                "startTimeLocal": "2026-10-23T07:00:00",
                "activityType": {"typeKey": "running"},
                "duration": 3600,
                "distance": 10000,
                "privateField": "excluded",
            },
            "not an activity",
        ]

        activities = await get_recent_activities(
            client,
            limit=20,
            start=5,
            start_date="2026-10-01",
            end_date="2026-10-23",
            activity_type="running",
        )

        self.assertEqual(activities, [{
            "activityId": 123,
            "activityName": "Morning Run",
            "startTimeLocal": "2026-10-23T07:00:00",
            "activityType": {"typeKey": "running"},
            "duration": 3600,
            "distance": 10000,
        }])
        client.get_json.assert_awaited_once_with(
            "/activitylist-service/activities/search/activities",
            params={
                "start": 5,
                "limit": 20,
                "startDate": "2026-10-01",
                "endDate": "2026-10-23",
                "activityType": "running",
            },
        )

    async def test_recent_activities_rejects_invalid_pagination_and_dates(self):
        client = AsyncMock()
        invalid_calls = (
            {"limit": 0},
            {"limit": 51},
            {"start": -1},
            {"start_date": "2026-10-01"},
            {"start_date": "2026-10-23", "end_date": "2026-10-01"},
        )
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    await get_recent_activities(client, **arguments)
        client.get_json.assert_not_awaited()

    async def test_activity_details_and_workouts(self):
        client = AsyncMock()
        client.get_json.side_effect = [{"activityId": 123}, [{"step": 1}]]

        details = await get_activity_details(client, 123)
        workouts = await get_activity_workouts(client, 123)

        self.assertEqual(details, {"activityId": 123})
        self.assertEqual(workouts, [{"step": 1}])
        self.assertEqual(
            client.get_json.await_args_list[0].args,
            ("/activity-service/activity/123",),
        )
        self.assertEqual(
            client.get_json.await_args_list[1].args,
            ("/activity-service/activity/123/workouts",),
        )

    async def test_activity_details_rejects_unexpected_response(self):
        client = AsyncMock()
        client.get_json.return_value = []
        with self.assertRaisesRegex(RuntimeError, "activity details"):
            await get_activity_details(client, 123)

    async def test_activity_functions_reject_non_positive_ids(self):
        client = AsyncMock()
        for function in (get_activity_details, get_activity_workouts):
            with self.subTest(function=function.__name__):
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    await function(client, 0)

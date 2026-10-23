import os
import unittest
from unittest.mock import patch

import httpx

import garmin_client
from garmin_client import GarminClient


class FakeAsyncClient:
    responses = []
    requests = []

    def __init__(self, timeout):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def post(self, url, headers):
        self.requests.append(("POST", url, headers, None))
        return self.responses.pop(0)

    async def get(self, url, headers, params=None):
        self.requests.append(("GET", url, headers.copy(), params))
        return self.responses.pop(0)


def response(status_code, *, text="", json=None):
    request = httpx.Request("GET", "https://example.test")
    if json is not None:
        return httpx.Response(status_code, json=json, request=request)
    return httpx.Response(status_code, content=text, request=request)


class GarminClientTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"GARMIN_PERSONAL_API_KEY": "test-key"})
        self.environment.start()
        FakeAsyncClient.responses = []
        FakeAsyncClient.requests = []

    def tearDown(self):
        self.environment.stop()

    def test_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "GARMIN_PERSONAL_API_KEY"):
                GarminClient()

    async def test_get_access_token_caches_token(self):
        FakeAsyncClient.responses = [response(200, text="access-token\n")]
        with patch.object(garmin_client.httpx, "AsyncClient", FakeAsyncClient):
            client = GarminClient()
            first = await client.get_access_token()
            second = await client.get_access_token()

        self.assertEqual((first, second), ("access-token", "access-token"))
        self.assertEqual(len(FakeAsyncClient.requests), 1)
        self.assertEqual(
            FakeAsyncClient.requests[0],
            ("POST", garmin_client.TOKEN_URL, {"Authorization": "ApiKey test-key"}, None),
        )

    async def test_get_json_refreshes_token_once_after_unauthorized_response(self):
        FakeAsyncClient.responses = [
            response(200, text="initial-token"),
            response(401, json={"message": "expired"}),
            response(200, text="fresh-token"),
            response(200, json={"value": 42}),
        ]
        with patch.object(garmin_client.httpx, "AsyncClient", FakeAsyncClient):
            client = GarminClient()
            data = await client.get_json("/resource", params={"date": "2026-10-23"})

        self.assertEqual(data, {"value": 42})
        get_requests = [request for request in FakeAsyncClient.requests if request[0] == "GET"]
        self.assertEqual(len(get_requests), 2)
        self.assertEqual(get_requests[0][2]["Authorization"], "Bearer initial-token")
        self.assertEqual(get_requests[1][2]["Authorization"], "Bearer fresh-token")
        self.assertEqual(get_requests[1][3], {"date": "2026-10-23"})

import asyncio
import os
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

GARMIN_API_BASE = "https://personal.connectapi.garmin.com"
TOKEN_URL = f"{GARMIN_API_BASE}/personalapitoken-service/personal-api/personal-api-key/token"
TOKEN_CACHE_SECONDS = 23 * 60 * 60 + 50 * 60


class GarminClient:
    """Authentication and shared HTTP transport for Garmin API services."""

    def __init__(self):
        self.api_key = os.getenv("GARMIN_PERSONAL_API_KEY")
        if not self.api_key:
            raise RuntimeError("GARMIN_PERSONAL_API_KEY is not configured")

        self._access_token: str | None = None
        self._token_expires_at = 0.0
        self._token_lock = asyncio.Lock()

    async def get_access_token(self, force_refresh: bool = False) -> str:
        async with self._token_lock:
            now = time.monotonic()
            if (
                not force_refresh
                and self._access_token
                and now < self._token_expires_at
            ):
                return self._access_token

            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    TOKEN_URL,
                    headers={"Authorization": f"ApiKey {self.api_key}"},
                )
            response.raise_for_status()
            token = response.text.strip()
            if not token:
                raise RuntimeError("Garmin returned an empty access token")

            self._access_token = token
            self._token_expires_at = time.monotonic() + TOKEN_CACHE_SECONDS
            return token

    async def get_json(
        self,
        path: str,
        params: dict | None = None,
        timeout: float = 30,
    ):
        """GET and decode a Garmin API resource, refreshing once on HTTP 401."""
        url = f"{GARMIN_API_BASE}/{path.lstrip('/')}"
        token = await self.get_access_token()
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code == 401:
                token = await self.get_access_token(force_refresh=True)
                headers["Authorization"] = f"Bearer {token}"
                response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

import unittest

import httpx
from mcp.server import MCPServer
from mcp.server.auth.provider import AccessToken

from auth.auth_config import Auth0Settings
from auth.mcp_auth import build_auth_settings


class StaticTokenVerifier:
    def __init__(self, token: AccessToken | None):
        self.token = token

    async def verify_token(self, raw_token: str) -> AccessToken | None:
        return self.token if raw_token == "valid-token" else None


class McpAuthTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.settings = Auth0Settings(
            domain="dev-example.eu.auth0.com",
            audience="https://garmin-mcp.example.com/mcp",
            server_url="https://garmin-mcp.example.com/mcp",
        )

    def create_app(self, scopes: list[str]):
        token = AccessToken(
            token="valid-token",
            client_id="chatgpt-client",
            subject="auth0|user-123",
            scopes=scopes,
            resource=self.settings.audience,
        )
        server = MCPServer(
            "Test Garmin MCP",
            auth=build_auth_settings(self.settings),
            token_verifier=StaticTokenVerifier(token),
        )
        return server.streamable_http_app(host="garmin-mcp.example.com")

    async def request(self, app, path, headers=None):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="https://garmin-mcp.example.com",
        ) as client:
            return await client.get(path, headers=headers)

    async def test_mcp_endpoint_rejects_requests_without_a_token(self):
        response = await self.request(self.create_app(["read:garmin"]), "/mcp")

        self.assertEqual(response.status_code, 401)
        self.assertIn("Authentication required", response.text)
        self.assertIn(
            'resource_metadata="https://garmin-mcp.example.com/.well-known/oauth-protected-resource/mcp"',
            response.headers["www-authenticate"],
        )

    async def test_mcp_endpoint_rejects_token_without_required_scope(self):
        response = await self.request(
            self.create_app([]),
            "/mcp",
            headers={"Authorization": "Bearer valid-token"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn("Required scope: read:garmin", response.text)

    async def test_protected_resource_metadata_advertises_auth0_and_scope(self):
        response = await self.request(
            self.create_app(["read:garmin"]),
            "/.well-known/oauth-protected-resource/mcp",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "resource": "https://garmin-mcp.example.com/mcp",
            "authorization_servers": ["https://dev-example.eu.auth0.com/"],
            "scopes_supported": ["read:garmin"],
            "bearer_methods_supported": ["header"],
        })

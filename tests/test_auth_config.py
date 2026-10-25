import unittest

from auth_config import AuthConfigurationError, load_auth0_settings


class Auth0ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.environment = {
            "AUTH0_DOMAIN": "dev-example.eu.auth0.com",
            "MCP_SERVER_URL": "https://garmin-mcp.example.com/mcp",
            "AUTH0_AUDIENCE": "https://garmin-mcp.example.com/mcp",
        }

    def test_loads_valid_configuration(self):
        settings = load_auth0_settings(self.environment)

        self.assertEqual(settings.domain, "dev-example.eu.auth0.com")
        self.assertEqual(settings.issuer_url, "https://dev-example.eu.auth0.com/")
        self.assertEqual(
            settings.jwks_url,
            "https://dev-example.eu.auth0.com/.well-known/jwks.json",
        )
        self.assertEqual(settings.required_scope, "read:garmin")

    def test_accepts_custom_scope(self):
        settings = load_auth0_settings(
            self.environment | {"AUTH0_REQUIRED_SCOPE": "read:fitness"}
        )

        self.assertEqual(settings.required_scope, "read:fitness")

    def test_rejects_missing_required_setting(self):
        environment = self.environment.copy()
        del environment["AUTH0_DOMAIN"]

        with self.assertRaisesRegex(AuthConfigurationError, "AUTH0_DOMAIN"):
            load_auth0_settings(environment)

    def test_rejects_invalid_domain(self):
        with self.assertRaisesRegex(AuthConfigurationError, "AUTH0_DOMAIN"):
            load_auth0_settings(self.environment | {"AUTH0_DOMAIN": "https://bad.example"})

    def test_rejects_non_https_urls(self):
        with self.assertRaisesRegex(AuthConfigurationError, "MCP_SERVER_URL"):
            load_auth0_settings(
                self.environment | {"MCP_SERVER_URL": "http://garmin-mcp.example.com/mcp"}
            )

    def test_rejects_audience_for_another_api(self):
        with self.assertRaisesRegex(AuthConfigurationError, "AUTH0_AUDIENCE"):
            load_auth0_settings(
                self.environment | {"AUTH0_AUDIENCE": "https://another-api.example.com"}
            )

    def test_rejects_server_url_without_mcp_path(self):
        with self.assertRaisesRegex(AuthConfigurationError, "end with /mcp"):
            load_auth0_settings(
                self.environment
                | {
                    "MCP_SERVER_URL": "https://garmin-mcp.example.com",
                    "AUTH0_AUDIENCE": "https://garmin-mcp.example.com",
                }
            )

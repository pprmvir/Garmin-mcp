"""Configuration for the Auth0-backed MCP authentication flow.

This module does not enable authentication yet. It prepares validated settings
for the token-verification phase.
"""

import os
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlparse


class AuthConfigurationError(ValueError):
    """Raised when the Auth0 settings are missing or invalid."""


@dataclass(frozen=True)
class Auth0Settings:
    domain: str
    audience: str
    server_url: str
    required_scope: str = "read:garmin"

    @property
    def issuer_url(self) -> str:
        return f"https://{self.domain}/"

    @property
    def jwks_url(self) -> str:
        return f"https://{self.domain}/.well-known/jwks.json"


def load_auth0_settings(environment: Mapping[str, str] | None = None) -> Auth0Settings:
    """Load and validate Auth0 settings without exposing any secret values."""
    environment = environment or os.environ
    required = ("AUTH0_DOMAIN", "AUTH0_AUDIENCE", "MCP_SERVER_URL")
    missing = [name for name in required if not environment.get(name)]
    if missing:
        names = ", ".join(missing)
        raise AuthConfigurationError(f"Missing Auth0 configuration: {names}")

    domain = environment["AUTH0_DOMAIN"].strip().removesuffix("/")
    if "://" in domain or "/" in domain or not domain:
        raise AuthConfigurationError(
            "AUTH0_DOMAIN must be a domain such as dev-example.eu.auth0.com"
        )

    server_url = _validate_https_url("MCP_SERVER_URL", environment["MCP_SERVER_URL"])
    audience = _validate_https_url("AUTH0_AUDIENCE", environment["AUTH0_AUDIENCE"])
    if audience != server_url:
        raise AuthConfigurationError(
            "AUTH0_AUDIENCE must exactly match MCP_SERVER_URL"
        )
    if not server_url.endswith("/mcp"):
        raise AuthConfigurationError("MCP_SERVER_URL must end with /mcp")

    required_scope = environment.get("AUTH0_REQUIRED_SCOPE", "read:garmin").strip()
    if not required_scope or " " in required_scope:
        raise AuthConfigurationError(
            "AUTH0_REQUIRED_SCOPE must be one OAuth scope, such as read:garmin"
        )

    return Auth0Settings(
        domain=domain,
        audience=audience,
        server_url=server_url,
        required_scope=required_scope,
    )


def _validate_https_url(name: str, value: str) -> str:
    parsed = urlparse(value.strip())
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise AuthConfigurationError(f"{name} must be an HTTPS URL")
    return value.strip().rstrip("/")

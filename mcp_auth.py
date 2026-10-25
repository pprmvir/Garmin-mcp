"""MCP OAuth resource-server settings."""

from mcp.server.auth.settings import AuthSettings

from auth_config import Auth0Settings


def build_auth_settings(settings: Auth0Settings) -> AuthSettings:
    """Configure this MCP endpoint as an Auth0-protected OAuth resource."""
    return AuthSettings(
        issuer_url=settings.issuer_url,
        resource_server_url=settings.server_url,
        required_scopes=[settings.required_scope],
        validate_token_resource=True,
    )

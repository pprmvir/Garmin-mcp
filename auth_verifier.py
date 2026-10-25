"""Auth0 JWT verification for the Garmin MCP resource server."""

import logging
from datetime import UTC, datetime
from typing import Protocol

import jwt
from mcp.server.auth.provider import AccessToken

from auth_config import Auth0Settings

logger = logging.getLogger(__name__)


class SigningKeyProvider(Protocol):
    def get_signing_key_from_jwt(self, token: str): ...


class Auth0TokenVerifier:
    """Verify Auth0-issued RS256 access tokens for this MCP server."""

    def __init__(
        self,
        settings: Auth0Settings,
        signing_key_provider: SigningKeyProvider | None = None,
    ):
        self.settings = settings
        self.signing_key_provider = signing_key_provider or jwt.PyJWKClient(
            settings.jwks_url
        )

    async def verify_token(self, token: str) -> AccessToken | None:
        """Return validated token information, or None when validation fails."""
        try:
            signing_key = self.signing_key_provider.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.settings.audience,
                issuer=self.settings.issuer_url,
                options={"require": ["exp", "iss", "aud", "sub"]},
            )
        except jwt.PyJWTError:
            logger.info("Rejected an invalid Auth0 access token")
            return None

        expires_at = int(claims["exp"])
        scopes = _extract_scopes(claims)
        subject = str(claims["sub"])
        client_id = str(claims.get("azp") or claims.get("client_id") or subject)

        return AccessToken(
            token=token,
            client_id=client_id,
            scopes=scopes,
            expires_at=expires_at,
            resource=self.settings.audience,
            subject=subject,
            claims={"iss": self.settings.issuer_url},
        )


def _extract_scopes(claims: dict) -> list[str]:
    scope_claim = claims.get("scope", "")
    if isinstance(scope_claim, str):
        return scope_claim.split()
    return []

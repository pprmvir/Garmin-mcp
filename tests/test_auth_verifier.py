import unittest
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

from auth_config import Auth0Settings
from auth_verifier import Auth0TokenVerifier


class StaticSigningKeyProvider:
    def __init__(self, public_key):
        self.public_key = public_key
        self.tokens = []

    def get_signing_key_from_jwt(self, token):
        self.tokens.append(token)
        return SimpleNamespace(key=self.public_key)


class Auth0TokenVerifierTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.settings = Auth0Settings(
            domain="dev-example.eu.auth0.com",
            audience="https://garmin-mcp.example.com/mcp",
            server_url="https://garmin-mcp.example.com/mcp",
        )

    def setUp(self):
        self.key_provider = StaticSigningKeyProvider(self.private_key.public_key())
        self.verifier = Auth0TokenVerifier(self.settings, self.key_provider)

    def create_token(self, **overrides):
        now = datetime.now(UTC)
        claims = {
            "sub": "auth0|user-123",
            "azp": "chatgpt-client",
            "iss": self.settings.issuer_url,
            "aud": self.settings.audience,
            "scope": "read:garmin",
            "exp": now + timedelta(minutes=15),
        }
        claims.update(overrides)
        return jwt.encode(claims, self.private_key, algorithm="RS256")

    async def test_accepts_valid_auth0_access_token(self):
        raw_token = self.create_token()

        token = await self.verifier.verify_token(raw_token)

        self.assertIsNotNone(token)
        self.assertEqual(token.client_id, "chatgpt-client")
        self.assertEqual(token.subject, "auth0|user-123")
        self.assertEqual(token.scopes, ["read:garmin"])
        self.assertEqual(token.resource, self.settings.audience)

    async def test_rejects_expired_token(self):
        raw_token = self.create_token(exp=datetime.now(UTC) - timedelta(seconds=1))

        self.assertIsNone(await self.verifier.verify_token(raw_token))

    async def test_rejects_token_for_another_audience(self):
        raw_token = self.create_token(aud="https://another-api.example.com")

        self.assertIsNone(await self.verifier.verify_token(raw_token))

    async def test_rejects_token_from_another_issuer(self):
        raw_token = self.create_token(iss="https://other-tenant.eu.auth0.com/")

        self.assertIsNone(await self.verifier.verify_token(raw_token))

    async def test_rejects_token_with_invalid_signature(self):
        untrusted_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        raw_token = jwt.encode(
            {
                "sub": "auth0|user-123",
                "iss": self.settings.issuer_url,
                "aud": self.settings.audience,
                "exp": datetime.now(UTC) + timedelta(minutes=15),
            },
            untrusted_key,
            algorithm="RS256",
        )

        self.assertIsNone(await self.verifier.verify_token(raw_token))

    async def test_returns_no_scopes_when_scope_claim_is_missing(self):
        raw_token = self.create_token()
        claims = jwt.decode(raw_token, options={"verify_signature": False})
        del claims["scope"]
        raw_token = jwt.encode(claims, self.private_key, algorithm="RS256")

        token = await self.verifier.verify_token(raw_token)

        self.assertIsNotNone(token)
        self.assertEqual(token.scopes, [])

    async def test_rejects_token_when_no_signing_key_is_available(self):
        class FailingKeyProvider:
            def get_signing_key_from_jwt(self, token):
                raise jwt.PyJWKClientError("Unknown signing key")

        verifier = Auth0TokenVerifier(self.settings, FailingKeyProvider())

        self.assertIsNone(await verifier.verify_token(self.create_token()))

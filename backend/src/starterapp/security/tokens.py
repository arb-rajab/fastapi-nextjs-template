"""Session-token issuance and verification.

HS256 JWTs signed with `Settings.jwt_secret_key`. This process is both the
issuer and the only verifier, so asymmetric keys would add key management
with no benefit. If a separate service must verify tokens, move to RS256
and publish a JWKS instead.
"""

from datetime import UTC, datetime, timedelta

import jwt

from starterapp.config import Settings

_ACCESS_CLAIM_TYPE = "access"


class InvalidToken(Exception):
    """Raised for any token that must not be trusted: bad signature, expired,
    wrong algorithm or type, or missing claims. Callers map this to a single
    401 and never reveal why, to avoid handing out a forgery oracle."""


def issue_access_token(user_id: str, settings: Settings) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "type": _ACCESS_CLAIM_TYPE,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_access_token(token: str, settings: Settings) -> str:
    """Returns the verified `sub` (user id) claim, or raises InvalidToken."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp", "iat", "type"]},
        )
    except jwt.PyJWTError as exc:
        raise InvalidToken(str(exc)) from exc

    if payload.get("type") != _ACCESS_CLAIM_TYPE:
        raise InvalidToken("unexpected token type")

    sub = payload["sub"]
    if not isinstance(sub, str) or not sub:
        raise InvalidToken("empty subject claim")
    return sub

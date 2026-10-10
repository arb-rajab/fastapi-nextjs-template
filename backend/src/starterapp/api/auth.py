"""Caller identity extraction.

A caller identity is only ever accepted from a cryptographically verified
session token (a `starterapp.security.tokens` JWT obtained from
`POST /api/v1/auth/login` or `/register`), presented as
`Authorization: Bearer <token>`. No request header can set the caller
identity directly.
"""

from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from starterapp.api.errors import api_error
from starterapp.config import Settings, get_settings
from starterapp.security.tokens import InvalidToken, verify_access_token

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CallerContext:
    user_id: str


def _unauthenticated() -> HTTPException:
    return api_error(
        401, "unauthenticated", "A valid Authorization: Bearer <token> header is required"
    )


def get_caller(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> CallerContext:
    if credentials is None or not credentials.credentials:
        raise _unauthenticated()
    try:
        user_id = verify_access_token(credentials.credentials, settings)
    except InvalidToken as exc:
        raise _unauthenticated() from exc
    return CallerContext(user_id=user_id)

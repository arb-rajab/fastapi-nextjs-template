"""Register, login and "who am I" endpoints. This module issues session
tokens; `starterapp.api.auth.get_caller` verifies them."""

import logging
import secrets

import redis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from starterapp.api.auth import CallerContext, get_caller
from starterapp.api.deps import get_db, get_redis
from starterapp.api.errors import api_error, conflict
from starterapp.api.rate_limit import (
    RateLimitExceeded,
    enforce_login_rate_limit,
    enforce_register_rate_limit,
)
from starterapp.api.schemas import LoginRequest, MeOut, RegisterRequest, TokenOut
from starterapp.config import get_settings
from starterapp.db import models
from starterapp.security.passwords import hash_password, verify_password
from starterapp.security.tokens import issue_access_token

logger = logging.getLogger("starterapp.auth")

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Hashed once at import time in the same format a real stored hash has, so
# `login` can run `verify_password` against it when the username does not
# exist. Skipping the PBKDF2 work for unknown users would make them respond
# measurably faster, which is a username-enumeration oracle.
_DUMMY_PASSWORD_HASH = hash_password(secrets.token_hex(32))


def _invalid_credentials() -> HTTPException:
    # Identical whether the username is unknown or the password is wrong.
    return api_error(401, "invalid_credentials", "Invalid username or password")


@router.post("/register", status_code=201, response_model=TokenOut)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> TokenOut:
    # `get_settings` is called directly (not via Depends) so a test can
    # monkeypatch this module's name to exercise a different threshold.
    settings = get_settings()
    try:
        enforce_register_rate_limit(redis_client, settings)
    except RateLimitExceeded as exc:
        raise api_error(
            429,
            "rate_limited",
            "Too many registration attempts",
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc

    username = payload.username.strip()
    if not username:
        raise api_error(422, "invalid_username", "Username cannot be blank", "username")

    user = models.AppUser(username=username, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise conflict("username_taken", "That username is already registered", "username") from exc

    token = issue_access_token(username, settings)
    return TokenOut(access_token=token, username=username)


@router.post("/login", response_model=TokenOut)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> TokenOut:
    settings = get_settings()
    try:
        enforce_login_rate_limit(redis_client, settings, payload.username)
    except RateLimitExceeded as exc:
        raise api_error(
            429,
            "rate_limited",
            "Too many login attempts",
            headers={"Retry-After": str(exc.retry_after)},
        ) from exc

    username = payload.username.strip()
    user = db.execute(select(models.AppUser).filter_by(username=username)).scalar_one_or_none()
    # Always run the PBKDF2 comparison so response time does not reveal
    # whether the username exists.
    password_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
    password_ok = verify_password(payload.password, password_hash)
    if user is None or not password_ok:
        raise _invalid_credentials()

    token = issue_access_token(user.username, settings)
    return TokenOut(access_token=token, username=user.username)


@router.get("/me", response_model=MeOut)
def me(caller: CallerContext = Depends(get_caller)) -> MeOut:
    return MeOut(username=caller.user_id)

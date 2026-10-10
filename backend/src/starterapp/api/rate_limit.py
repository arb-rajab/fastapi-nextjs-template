"""Redis-backed fixed-window rate limiting for the auth endpoints.

Every limiter fails OPEN on a Redis outage (logged, not raised): an
unreachable rate-limit backend should not itself take login down. Copy
`_enforce_fixed_window` for other endpoints that need a throttle.
"""

import logging

import redis

from starterapp.config import Settings

logger = logging.getLogger("starterapp.rate_limit")

_LOGIN_WINDOW_SECONDS = 5 * 60
_REGISTER_WINDOW_SECONDS = 5 * 60
_REGISTER_KEY = "starterapp:register-attempts:global"


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(f"rate limit exceeded, retry after {retry_after}s")


def _enforce_fixed_window(
    redis_client: redis.Redis, key: str, limit: int, window_seconds: int, what: str
) -> None:
    try:
        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, window_seconds)
        if count > limit:
            ttl = redis_client.ttl(key)
            raise RateLimitExceeded(retry_after=ttl if ttl and ttl > 0 else window_seconds)
    except redis.RedisError:
        logger.warning("%s rate limiter unreachable, failing open for this request", what)


def enforce_login_rate_limit(redis_client: redis.Redis, settings: Settings, username: str) -> None:
    """Keyed by the submitted username (the caller IP is not reliably visible
    behind an unknown proxy layer)."""
    _enforce_fixed_window(
        redis_client,
        f"starterapp:login-attempts:{username.strip().lower()}",
        settings.login_rate_limit_per_5_minutes,
        _LOGIN_WINDOW_SECONDS,
        "login",
    )


def enforce_register_rate_limit(redis_client: redis.Redis, settings: Settings) -> None:
    """Global bucket: the identity being registered does not exist yet, so a
    per-username key could be evaded by varying the username."""
    _enforce_fixed_window(
        redis_client,
        _REGISTER_KEY,
        settings.register_rate_limit_per_5_minutes,
        _REGISTER_WINDOW_SECONDS,
        "register",
    )

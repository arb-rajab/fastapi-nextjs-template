from functools import lru_cache

import redis

from starterapp.config import get_settings
from starterapp.db.session import get_db


@lru_cache
def _cached_redis_client() -> redis.Redis:
    # One connection pool per process, not one client per request.
    return redis.Redis.from_url(get_settings().redis_url, decode_responses=True)


def get_redis() -> redis.Redis:
    return _cached_redis_client()


__all__ = ["get_db", "get_redis"]

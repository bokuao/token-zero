"""
Simple in-memory cache for API responses.
TTL 30 detik — reduce DB load, stale on expiry.
"""

import time
import threading
import functools
from typing import Callable

_cache: dict[str, tuple[float, object]] = {}
_lock = threading.Lock()
TTL = 30  # detik


def cached(ttl: int = TTL):
    """Decorator: cache function result in-memory for `ttl` seconds."""

    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key = f"{fn.__name__}:{args}:{kwargs}"
            now = time.time()

            with _lock:
                entry = _cache.get(key)
                if entry and (now - entry[0]) < ttl:
                    return entry[1]

            result = fn(*args, **kwargs)
            with _lock:
                _cache[key] = (time.time(), result)
            return result

        return wrapper

    return decorator

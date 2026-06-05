"""
Health check untuk provider — cek base_url reachable tanpa API key.
- Cache 5 menit
- Stale-while-revalidate: kalau expired, return data lama sambil refresh di background
- Thundering herd protection: hanya 1 request yg trigger refresh
"""

import time
import threading
import httpx
import logging

logger = logging.getLogger(__name__)

TIMEOUT = 5       # detik timeout per provider
CACHE_TTL = 300   # 5 menit
STALE_TTL = 600   # 10 menit — masih boleh return stale

_cache: dict[str, dict] = {}
_lock = threading.Lock()
_refreshing: set[str] = set()


def check_provider_health(base_url: str) -> dict:
    """Cek provider reachable (no API key)."""
    url = f"{base_url.rstrip('/')}/models"
    try:
        start = time.time()
        with httpx.Client(timeout=TIMEOUT) as client:
            resp = client.get(url)
        elapsed = (time.time() - start) * 1000
        healthy = resp.status_code in (200, 401, 403)
        return {
            "healthy": healthy,
            "status": resp.status_code,
            "latency_ms": round(elapsed, 0),
        }
    except (httpx.ConnectError, httpx.TimeoutException):
        return {"healthy": False, "status": None, "latency_ms": None}
    except Exception as e:
        logger.warning(f"Health check error for {base_url}: {e}")
        return {"healthy": False, "status": None, "latency_ms": None}


def get_cached_health(provider_id: str, base_url: str) -> dict:
    """
    Get health with thundering herd protection:
    - Fresh cache (<5m): return immediately
    - Stale cache (5-10m): return stale, trigger background refresh
    - No cache / >10m: wait for fresh result (block)
    """
    now = time.time()

    with _lock:
        entry = _cache.get(provider_id)

        # Fresh — return immediately
        if entry and (now - entry["ts"]) < CACHE_TTL:
            return entry["data"]

        # Stale but usable — return now, refresh in background
        if entry and (now - entry["ts"]) < STALE_TTL:
            if provider_id not in _refreshing:
                _refreshing.add(provider_id)
                threading.Thread(
                    target=_background_refresh,
                    args=(provider_id, base_url),
                    daemon=True,
                ).start()
            return entry["data"]

        # Nothing usable — block until fresh
        if provider_id in _refreshing:
            pass  # Another thread is already fetching; release lock and wait below

    # Slow path: fetch synchronously (only one thread at a time per provider)
    with _lock:
        # Double-check: another thread might have finished while we waited
        entry = _cache.get(provider_id)
        if entry and (now - entry["ts"]) < CACHE_TTL:
            return entry["data"]

        _refreshing.add(provider_id)

    try:
        data = check_provider_health(base_url)
        with _lock:
            _cache[provider_id] = {"ts": time.time(), "data": data}
            _refreshing.discard(provider_id)
        return data
    except Exception:
        with _lock:
            _refreshing.discard(provider_id)
        # If we have stale data, return it as last resort
        entry = _cache.get(provider_id)
        if entry:
            return entry["data"]
        return {"healthy": False, "status": None, "latency_ms": None}


def _background_refresh(provider_id: str, base_url: str):
    """Refresh cache in background thread."""
    try:
        data = check_provider_health(base_url)
        with _lock:
            _cache[provider_id] = {"ts": time.time(), "data": data}
    except Exception:
        pass
    finally:
        with _lock:
            _refreshing.discard(provider_id)

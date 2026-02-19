import threading
from cachetools import TTLCache
from config import CACHE_TTL_CAMERAS, CACHE_TTL_STATS, CACHE_TTL_ARCHIVES, CACHE_TTL_HEALTH

_lock = threading.Lock()

_cameras_cache = TTLCache(maxsize=2, ttl=CACHE_TTL_CAMERAS)
_stats_cache = TTLCache(maxsize=2, ttl=CACHE_TTL_STATS)
_archives_cache = TTLCache(maxsize=20, ttl=CACHE_TTL_ARCHIVES)
_health_cache = TTLCache(maxsize=2, ttl=CACHE_TTL_HEALTH)


def get_cameras(client) -> list[dict]:
    with _lock:
        if "all" not in _cameras_cache:
            _cameras_cache["all"] = client.get_all_cameras()
        return _cameras_cache["all"]


def get_health(client) -> dict:
    with _lock:
        if "h" not in _health_cache:
            try:
                _health_cache["h"] = client.get_health()
            except Exception:
                _health_cache["h"] = {"status": "error"}
        return _health_cache["h"]


def get_stats(client, compute_fn) -> dict:
    with _lock:
        if "s" not in _stats_cache:
            cameras = get_cameras.__wrapped__(client) if hasattr(get_cameras, '__wrapped__') else get_cameras(client)
            _stats_cache["s"] = compute_fn(cameras)
        return _stats_cache["s"]


def invalidate_cameras():
    with _lock:
        _cameras_cache.clear()
        _stats_cache.clear()


def get_cached_archives(client, key: str, fetch_fn) -> dict:
    with _lock:
        if key not in _archives_cache:
            _archives_cache[key] = fetch_fn()
        return _archives_cache[key]

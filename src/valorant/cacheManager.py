from typing import TYPE_CHECKING, Any, Dict, Optional
from time import time

if TYPE_CHECKING:
    from session import Session


class CacheData:
    def __init__(self, cache_data: Any, expires_at: int):
        self.cache_data = cache_data
        self.expires_at = expires_at


class CacheManager:
    def __init__(self, session: "Session", default_caching_seconds: int = 10800):
        self.session = session
        self.cache: Dict[str, CacheData] = {}
        self.default_caching_seconds = default_caching_seconds

    def add_to_cache(self, cache_key: str, cache_data: Any, cache_seconds: int = None):
        if cache_seconds is None:
            cache_seconds = self.default_caching_seconds

        self.cache[cache_key] = CacheData(cache_data, (time()+cache_seconds) if cache_seconds != -1 else -1)

    def remove_from_cache(self, cache_key: str):
        del self.cache[cache_key]

    def get_from_cache(self, cache_key):
        if cache_key not in self.cache:
            return None

        data = self.cache[cache_key]

        if time() > data.expires_at and data.expires_at != -1:
            self.remove_from_cache(cache_key)
            return None

        return data.cache_data

    def clean_cache(self):
        to_remove = []

        for key, value in self.cache.items():
            if time() < value.expires_at or value.expires_at == -1:
                continue

            to_remove.append(key)

        for key in to_remove:
            self.remove_from_cache(key)

    def clear_cache(self):
        self.cache.clear()

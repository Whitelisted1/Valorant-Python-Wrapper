from typing import TYPE_CHECKING, Any, Dict, Optional
from time import time

if TYPE_CHECKING:
    from .session import Session


class CacheData:
    def __init__(self, cache_data: Any, expires_at: int):
        """
        Represents data stored using the CacheManager. Contains the expiration date for the cached item

        Parameters:
        cache_data (Any): The data to store
        expires_at (int): The unix timestamp that this item expires at
        """

        self.cache_data = cache_data
        self.expires_at = expires_at


class CacheManager:
    def __init__(self, session: "Session", default_caching_seconds: int = 10800):
        """
        Stores cached keys and values for the specified amount of time

        Parameters:
        session (Session): The Session object
        default_caching_seconds (int): The default amount of time, in seconds, that an item will stay in the cache
        """

        self.session = session
        self.cache: Dict[str, CacheData] = {}
        self.default_caching_seconds = default_caching_seconds

    def add_to_cache(self, cache_key: str, cache_data: Any, cache_seconds: Optional[int] = None) -> None:
        """
        Adds a key and value to the cache for the specified amount of time

        Parameters:
        cache_key (str): The key that the cache_data will be stored under
        cache_data (Any): The data that will be stored under the cache_key
        cache_seconds (int, optional, defaults to None): The amount of time, in seconds, that the data will be stored for. Defaults to self.default_caching_seconds. If value is -1 the key will not expire
        """

        if cache_seconds is None:
            cache_seconds = self.default_caching_seconds

        self.cache[cache_key] = CacheData(cache_data, (time()+cache_seconds) if cache_seconds != -1 else -1)

    def remove_from_cache(self, cache_key: str) -> None:
        """
        Removes an item from the cache

        Parameters:
        cache_key (str): The cache key to be removed
        """

        del self.cache[cache_key]

    def get_from_cache(self, cache_key: str) -> Any:
        """
        Grabs an item from the cache by the key

        Parameters:
        cache_key (str): The key to grab from the cache

        Returns:
        Any: The data stored under the given key
        """

        # check to see if the key exists in the cache
        if cache_key not in self.cache:
            return None

        # grab the data
        data = self.cache[cache_key]

        # remove the item from the cache if it has expired
        if time() > data.expires_at and data.expires_at != -1:
            self.remove_from_cache(cache_key)
            return None

        return data.cache_data

    def clean_cache(self):
        """
        Goes through the cache and removes any items that have expired
        """

        # a list with the keys that need to be removed
        to_remove = []

        # go through the items and add them to to_remove if they have expired
        for key, value in self.cache.items():
            # skip items with an expiration date of -1
            if time() < value.expires_at or value.expires_at == -1:
                continue

            to_remove.append(key)

        # actually remove the data from the cache
        for key in to_remove:
            self.remove_from_cache(key)

    def clear_cache(self):
        """
        Removes all items from the cache
        """

        self.cache.clear()

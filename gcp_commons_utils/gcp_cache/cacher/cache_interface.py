"""Interface to implement necessary methods to work with cache_def."""
from abc import ABCMeta, abstractmethod
from typing import Any


class CacherInterface(metaclass=ABCMeta):
    """Cache Interface for GCP cache system."""

    @abstractmethod
    def get_cache(self, seed: str, cache_hash: str, seconds_expire: int) -> Any:
        """Retrieve the cache based on the received seed and cache_hash."""
        pass

    @abstractmethod
    def set_cache(self, seed: str, cache_hash: str, element: Any) -> bool:
        """Save the cache, with a given seed and cache_hash."""
        pass

    @abstractmethod
    def clear_cache(self, seed: str) -> bool:
        """Remove a specific cache based on a given seed."""
        pass

    @abstractmethod
    def clear_all_cache(self) -> bool:
        """Remove all cache from the cacher."""
        pass

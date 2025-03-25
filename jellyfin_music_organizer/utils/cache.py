import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, Generic, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class CacheEntry(Generic[V]):
    """Type-safe cache entry."""

    def __init__(self, value: V, ttl: Optional[timedelta] = None) -> None:
        self.value = value
        self.timestamp = datetime.now()
        self.ttl = ttl

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl is None:
            return False
        return datetime.now() - self.timestamp > self.ttl


class Cache(Generic[K, V]):
    """Thread-safe cache implementation."""

    def __init__(self, default_ttl: Optional[timedelta] = None) -> None:
        self._cache: Dict[K, CacheEntry[V]] = {}
        self._lock = threading.RLock()
        self.default_ttl = default_ttl
        self.logger = logging.getLogger(__name__)

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Get a value from the cache."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return default
            if entry.is_expired():
                del self._cache[key]
                return default
            return entry.value

    def set(self, key: K, value: V, ttl: Optional[timedelta] = None) -> None:
        """Set a value in the cache."""
        with self._lock:
            self._cache[key] = CacheEntry(value, ttl or self.default_ttl)

    def delete(self, key: K) -> None:
        """Delete a value from the cache."""
        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()

    def cleanup(self) -> None:
        """Remove expired entries."""
        with self._lock:
            expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]
            for key in expired_keys:
                del self._cache[key]

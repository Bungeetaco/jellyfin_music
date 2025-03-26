"""
Performance optimization utilities for the Jellyfin Music Organizer application.
"""

import json
import logging
import os
from functools import lru_cache, wraps
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Dict, List, Optional

from .logger import setup_logger

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages caching for frequently accessed data.

    This class:
    1. Provides file-based caching
    2. Manages cache invalidation
    3. Handles cache persistence
    """

    def __init__(self, cache_dir: str = ".cache") -> None:
        """
        Initialize the cache manager.

        Args:
            cache_dir: Directory for cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = setup_logger()

    def get_cached_data(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached data.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found
        """
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
                    self.logger.error("Cached data is not a dictionary")
                    return None
            except Exception as e:
                self.logger.error(f"Error reading cache: {e}")
        return None

    def set_cached_data(self, key: str, data: Dict[str, Any]) -> None:
        """
        Set cached data.

        Args:
            key: Cache key
            data: Data to cache
        """
        cache_file = self.cache_dir / f"{key}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            self.logger.error(f"Error writing cache: {e}")

    def invalidate_cache(self, key: str) -> None:
        """
        Invalidate cached data.

        Args:
            key: Cache key
        """
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                cache_file.unlink()
            except Exception as e:
                self.logger.error(f"Error invalidating cache: {e}")


class BatchProcessor:
    """
    Processes items in batches for better performance.

    This class:
    1. Handles batch processing
    2. Provides progress tracking
    3. Manages memory usage
    """

    def __init__(self, batch_size: int = 100) -> None:
        """
        Initialize the batch processor.

        Args:
            batch_size: Number of items to process in each batch
        """
        self.batch_size = batch_size
        self.logger = setup_logger()

    def process_batch(self, items: List[Any], processor: Callable[[Any], Any]) -> List[Any]:
        """
        Process items in batches.

        Args:
            items: List of items to process
            processor: Function to process each item

        Returns:
            List of processed items
        """
        results = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i : i + self.batch_size]
            try:
                batch_results = [processor(item) for item in batch]
                results.extend(batch_results)
            except Exception as e:
                self.logger.error(f"Error processing batch: {e}")
        return results


@lru_cache(maxsize=1000)
def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Get cached file information.

    Args:
        file_path: Path to file

    Returns:
        Dictionary containing file information
    """
    path = Path(file_path)
    return {
        "size": path.stat().st_size,
        "modified": path.stat().st_mtime,
        "created": path.stat().st_ctime,
    }


class PerformanceMonitor:
    """Monitor and log performance metrics."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, float] = {}
        self.start_times: Dict[str, float] = {}

    def start(self, operation: str) -> None:
        """Start timing an operation."""
        self.start_times[operation] = perf_counter()

    def stop(self, operation: str) -> Optional[float]:
        """Stop timing an operation and return duration."""
        try:
            start_time = self.start_times.pop(operation)
            duration = perf_counter() - start_time
            self.metrics[operation] = duration
            return duration
        except KeyError:
            self.logger.warning(f"No start time found for operation: {operation}")
            return None

    def get_metrics(self) -> Dict[str, float]:
        """Get all collected metrics."""
        return self.metrics.copy()

    @staticmethod
    def timed(operation_name: str) -> Callable:
        """Decorator for timing function execution."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start = perf_counter()
                try:
                    result = func(*args, **kwargs)
                    duration = perf_counter() - start
                    logging.getLogger(__name__).debug(
                        f"{operation_name} took {duration:.3f} seconds"
                    )
                    return result
                except Exception as e:
                    duration = perf_counter() - start
                    logging.getLogger(__name__).error(
                        f"{operation_name} failed after {duration:.3f} seconds: {e}"
                    )
                    raise

            return wrapper

        return decorator

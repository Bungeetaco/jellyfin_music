"""
Performance optimization utilities for the Jellyfin Music Organizer application.
"""

import os
import time
from typing import Dict, Any, Optional, List, Callable
from functools import lru_cache
from pathlib import Path
from .exceptions import FileOperationError
from .logger import setup_logger

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
                import json
                with open(cache_file, 'r') as f:
                    return json.load(f)
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
            import json
            with open(cache_file, 'w') as f:
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
            batch = items[i:i + self.batch_size]
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
        "created": path.stat().st_ctime
    }

class PerformanceMonitor:
    """
    Monitors application performance.
    
    This class:
    1. Tracks execution time
    2. Monitors memory usage
    3. Provides performance metrics
    """
    
    def __init__(self) -> None:
        """Initialize the performance monitor."""
        self.start_time: Optional[float] = None
        self.logger = setup_logger()
        
    def start(self) -> None:
        """Start performance monitoring."""
        self.start_time = time.time()
        
    def stop(self) -> float:
        """
        Stop performance monitoring.
        
        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            return 0.0
        elapsed = time.time() - self.start_time
        self.start_time = None
        return elapsed
        
    def log_performance(self, operation: str, elapsed: float) -> None:
        """
        Log performance metrics.
        
        Args:
            operation: Name of the operation
            elapsed: Elapsed time in seconds
        """
        self.logger.info(f"Performance: {operation} took {elapsed:.2f} seconds") 
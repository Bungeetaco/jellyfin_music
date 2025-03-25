"""
Progress tracking for the Jellyfin Music Organizer application.
"""

from typing import Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProgressInfo:
    """Information about the current progress."""
    current: int
    total: int
    start_time: datetime
    current_item: Optional[str] = None
    status: str = ""

class ProgressTracker:
    """
    Tracks progress of long-running operations.
    
    This class:
    1. Tracks current progress
    2. Calculates completion time
    3. Provides progress callbacks
    """
    
    def __init__(self, total: int, callback: Optional[Callable[[ProgressInfo], Any]] = None) -> None:
        """
        Initialize the progress tracker.
        
        Args:
            total: Total number of items to process
            callback: Optional callback function for progress updates
        """
        self.total = total
        self.current = 0
        self.start_time = datetime.now()
        self.callback = callback
        self.current_item: Optional[str] = None
        self.status = "Starting..."
        
    def update(self, current: int, item: Optional[str] = None, status: Optional[str] = None) -> None:
        """
        Update the current progress.
        
        Args:
            current: Current progress value
            item: Current item being processed
            status: Current status message
        """
        self.current = current
        if item is not None:
            self.current_item = item
        if status is not None:
            self.status = status
            
        if self.callback:
            self.callback(self.get_progress_info())
            
    def increment(self, item: Optional[str] = None, status: Optional[str] = None) -> None:
        """
        Increment the progress counter.
        
        Args:
            item: Current item being processed
            status: Current status message
        """
        self.update(self.current + 1, item, status)
        
    def get_progress_info(self) -> ProgressInfo:
        """
        Get current progress information.
        
        Returns:
            ProgressInfo object with current progress details
        """
        return ProgressInfo(
            current=self.current,
            total=self.total,
            start_time=self.start_time,
            current_item=self.current_item,
            status=self.status
        )
        
    def get_percentage(self) -> float:
        """
        Get the current progress percentage.
        
        Returns:
            Progress percentage as float between 0 and 100
        """
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100
        
    def get_elapsed_time(self) -> float:
        """
        Get the elapsed time in seconds.
        
        Returns:
            Elapsed time in seconds
        """
        return (datetime.now() - self.start_time).total_seconds()
        
    def get_estimated_time_remaining(self) -> Optional[float]:
        """
        Get the estimated time remaining in seconds.
        
        Returns:
            Estimated time remaining in seconds, or None if progress is 0
        """
        if self.current == 0:
            return None
        elapsed = self.get_elapsed_time()
        rate = self.current / elapsed
        remaining = self.total - self.current
        return remaining / rate if rate > 0 else None 
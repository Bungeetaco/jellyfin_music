from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import logging
import threading

@dataclass
class Event:
    """Analytics event."""
    name: str
    timestamp: datetime
    data: Dict[str, Any]
    category: str

class Analytics:
    """Analytics tracking system."""
    
    def __init__(self, storage_path: Path) -> None:
        self.logger = logging.getLogger(__name__)
        self._storage_path = storage_path
        self._events: List[Event] = []
        self._lock = threading.Lock()
        self._enabled = True

    def track_event(
        self,
        name: str,
        category: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track an analytics event."""
        if not self._enabled:
            return

        event = Event(
            name=name,
            timestamp=datetime.now(),
            data=data or {},
            category=category
        )

        with self._lock:
            self._events.append(event)
            if len(self._events) >= 100:  # Batch size
                self._save_events()

    def _save_events(self) -> None:
        """Save events to storage."""
        try:
            events_data = [
                {
                    "name": event.name,
                    "timestamp": event.timestamp.isoformat(),
                    "data": event.data,
                    "category": event.category
                }
                for event in self._events
            ]

            file_path = self._storage_path / f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, indent=2)

            self._events.clear()
        except Exception as e:
            self.logger.error(f"Failed to save analytics events: {e}")

    def enable(self) -> None:
        """Enable analytics tracking."""
        self._enabled = True

    def disable(self) -> None:
        """Disable analytics tracking."""
        self._enabled = False

    def cleanup(self) -> None:
        """Save remaining events and cleanup."""
        with self._lock:
            if self._events:
                self._save_events() 
import logging
from typing import Any, Callable, Dict, Generic, TypeVar, List, Optional
from dataclasses import dataclass

from PyQt5.QtCore import QObject, pyqtSignal

T = TypeVar("T")

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Type-safe event implementation."""

    def __init__(self) -> None:
        self._handlers: List[Callable[[T], None]] = []

    def connect(self, handler: Callable[[T], None]) -> None:
        """Connect an event handler."""
        self._handlers.append(handler)

    def disconnect(self, handler: Callable[[T], None]) -> None:
        """Disconnect an event handler."""
        if handler in self._handlers:
            self._handlers.remove(handler)

    def emit(self, data: T) -> None:
        """Emit event to all handlers."""
        for handler in self._handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")


class EventManager(QObject):
    """Manage application events."""

    error_occurred = pyqtSignal(str)
    state_changed = pyqtSignal(dict)
    task_completed = pyqtSignal(str, bool)

    def __init__(self) -> None:
        super().__init__()
        self._events: Dict[str, Event[Any]] = {}

    def register_event(self, event_name: str) -> None:
        """Register a new event type."""
        if event_name not in self._events:
            self._events[event_name] = Event()

    def emit_event(self, event_name: str, data: Any) -> None:
        """Emit an event with data."""
        if event_name in self._events:
            self._events[event_name].emit(data)
        else:
            logger.warning(f"Unknown event: {event_name}")

    def connect_event(self, event_name: str, handler: Callable[[Any], None]) -> None:
        """Connect a handler to an event."""
        if event_name in self._events:
            self._events[event_name].connect(handler)
        else:
            logger.warning(f"Cannot connect to unknown event: {event_name}")

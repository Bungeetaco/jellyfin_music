import json
import logging
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


@dataclass
class StateChange(Generic[T]):
    """Represents a state change event."""

    key: str
    old_value: Optional[T]
    new_value: Optional[T]


class StateManager(Generic[T]):
    """Thread-safe application state management."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._state: Dict[str, T] = {}
        self._lock = RLock()
        self._observers: Dict[str, List[Callable[[StateChange[T]], None]]] = {}

    def set(self, key: str, value: T) -> None:
        """Set a state value."""
        with self._lock:
            old_value = self._state.get(key)
            self._state[key] = value
            self._notify_observers(StateChange(key, old_value, value))

    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Get a state value."""
        with self._lock:
            return self._state.get(key, default)

    def delete(self, key: str) -> None:
        """Delete a state value."""
        with self._lock:
            if key in self._state:
                old_value = self._state[key]
                del self._state[key]
                self._notify_observers(StateChange(key, old_value, None))

    def observe(self, key: str, callback: Callable[[StateChange[T]], None]) -> None:
        """Register a state change observer."""
        with self._lock:
            if key not in self._observers:
                self._observers[key] = []
            self._observers[key].append(callback)

    def _notify_observers(self, change: StateChange[T]) -> None:
        """Notify observers of state changes."""
        observers = self._observers.get(change.key, [])
        for observer in observers:
            try:
                observer(change)
            except Exception as e:
                self.logger.error(f"Observer error for {change.key}: {e}")

    def save_state(self, file_path: Path) -> bool:
        """Save state to file."""
        try:
            with self._lock:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self._state, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
            return False

    def load_state(self, file_path: Path) -> bool:
        """Load state from file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                with self._lock:
                    self._state = json.load(f)
            return True
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            return False

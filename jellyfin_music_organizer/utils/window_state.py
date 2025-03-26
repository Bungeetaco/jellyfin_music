"""Window state management utilities."""

import logging
from functools import wraps
from typing import Any, Callable, Dict, TypeVar

from PyQt5.QtCore import QByteArray, QSettings
from PyQt5.QtWidgets import QWidget

from .error_handler import handle_errors

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=QWidget)


class WindowStateManager:
    """Manage window state persistence with type safety."""

    def __init__(self, window_name: str) -> None:
        """Initialize the window state manager.

        Args:
            window_name: Unique identifier for the window
        """
        self.window_name = window_name
        self.settings = QSettings()
        self._state_cache: Dict[str, Any] = {}

    def save_state(self, window: T) -> bool:
        """Save window geometry and state.

        Args:
            window: Window instance to save state for

        Returns:
            bool: True if state was saved successfully
        """

        @handle_errors(logger=logger)
        def _save() -> bool:
            geometry = window.saveGeometry()
            if isinstance(geometry, QByteArray):
                self.settings.setValue(f"{self.window_name}/geometry", geometry)

            if hasattr(window, "saveState"):
                state = window.saveState()
                if isinstance(state, QByteArray):
                    self.settings.setValue(f"{self.window_name}/windowState", state)

            # Cache current settings
            self._state_cache = self._get_current_state()
            return True

        return _save()

    def restore_state(self, window: T) -> bool:
        """Restore window geometry and state.

        Args:
            window: Window instance to restore state for

        Returns:
            bool: True if state was restored successfully
        """

        @handle_errors(logger=logger)
        def _restore() -> bool:
            restored = False

            geometry = self.settings.value(f"{self.window_name}/geometry")
            if isinstance(geometry, QByteArray):
                restored = window.restoreGeometry(geometry)

            if hasattr(window, "restoreState"):
                state = self.settings.value(f"{self.window_name}/windowState")
                if isinstance(state, QByteArray):
                    restored = window.restoreState(state) and restored

            return restored

        return _restore()

    def _get_current_state(self) -> Dict[str, Any]:
        """Get current window state as dictionary."""
        return {
            "geometry": self.settings.value(f"{self.window_name}/geometry"),
            "windowState": self.settings.value(f"{self.window_name}/windowState"),
        }

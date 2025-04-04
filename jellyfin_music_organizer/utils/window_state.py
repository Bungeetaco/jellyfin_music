"""Window state management utilities."""

import logging
from typing import Any, Dict, TypeVar

from PyQt5.QtCore import QByteArray, QSettings
from PyQt5.QtWidgets import QWidget

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
        try:
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
        except Exception as e:
            logger.error(f"Failed to save window state: {e}")
            return False

    def restore_state(self, window: T) -> bool:
        """Restore window geometry and state.

        Args:
            window: Window instance to restore state for

        Returns:
            bool: True if state was restored successfully
        """
        try:
            restored = False

            geometry = self.settings.value(f"{self.window_name}/geometry")
            if isinstance(geometry, QByteArray):
                restored = window.restoreGeometry(geometry)

            if hasattr(window, "restoreState"):
                state = self.settings.value(f"{self.window_name}/windowState")
                if isinstance(state, QByteArray):
                    restored = window.restoreState(state) and restored

            return restored
        except Exception as e:
            logger.error(f"Failed to restore window state: {e}")
            return False

    def _get_current_state(self) -> Dict[str, Any]:
        """Get current window state as dictionary."""
        return {
            "geometry": self.settings.value(f"{self.window_name}/geometry"),
            "windowState": self.settings.value(f"{self.window_name}/windowState"),
        }

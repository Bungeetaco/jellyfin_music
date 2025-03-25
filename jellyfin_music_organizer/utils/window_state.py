"""Window state management utilities."""

<<<<<<< HEAD
from typing import Any, Dict, Optional
from pathlib import Path
import json
import logging
from PyQt5.QtCore import QSettings, QByteArray
from PyQt5.QtWidgets import QWidget

logger = logging.getLogger(__name__)

=======

from PyQt5.QtCore import QByteArray, QSettings
from PyQt5.QtWidgets import QWidget

>>>>>>> a450786950d6b878d67323779c3c958691fbf36f

class WindowStateManager:
    """Manage window state persistence."""

    def __init__(self, window_name: str) -> None:
        """Initialize the window state manager.

        Args:
            window_name: Unique identifier for the window
        """
        self.window_name = window_name
        self.settings = QSettings()

    def save_state(self, window: QWidget) -> None:
        """Save window geometry and state.

        Args:
            window: Window instance to save state for
        """
        try:
<<<<<<< HEAD
            self.settings.setValue(
                f"{self.window_name}/geometry",
                window.saveGeometry(),
            )
            if hasattr(window, "saveState"):
                self.settings.setValue(
                    f"{self.window_name}/windowState",
                    window.saveState(),
                )
=======
            self.settings.setValue(f"{self.window_name}/geometry", window.saveGeometry())
            if hasattr(window, "saveState"):
                self.settings.setValue(f"{self.window_name}/windowState", window.saveState())
>>>>>>> a450786950d6b878d67323779c3c958691fbf36f
        except Exception as e:
            logger.error(f"Failed to save window state: {e}")

    def restore_state(self, window: QWidget) -> bool:
        """Restore window geometry and state.

        Args:
            window: Window instance to restore state for

        Returns:
            bool: True if state was restored successfully
        """
        try:
            geometry = self.settings.value(f"{self.window_name}/geometry")
            state = self.settings.value(f"{self.window_name}/windowState")

            if geometry and isinstance(geometry, QByteArray):
                window.restoreGeometry(geometry)
            if state and isinstance(state, QByteArray):
                if hasattr(window, "restoreState"):
                    window.restoreState(state)
            return True
        except Exception as e:
            logger.error(f"Failed to restore window state: {e}")
            return False

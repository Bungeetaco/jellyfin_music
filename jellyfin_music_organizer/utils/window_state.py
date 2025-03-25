"""Window state management utilities."""


from PyQt5.QtCore import QByteArray, QSettings
from PyQt5.QtWidgets import QWidget


class WindowStateManager:
    """Manage window state persistence."""

    def __init__(self, window_name: str) -> None:
        self.window_name = window_name
        self.settings = QSettings()

    def save_state(self, window: QWidget) -> None:
        """Save window geometry and state."""
        try:
            self.settings.setValue(f"{self.window_name}/geometry", window.saveGeometry())
            if hasattr(window, "saveState"):
                self.settings.setValue(f"{self.window_name}/windowState", window.saveState())
        except Exception as e:
            logger.error(f"Failed to save window state: {e}")

    def restore_state(self, window: QWidget) -> bool:
        """Restore window geometry and state."""
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

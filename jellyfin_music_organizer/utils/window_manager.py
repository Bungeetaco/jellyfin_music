"""Window management utilities."""

from typing import Dict, Optional, Type
import logging

from PyQt5.QtWidgets import QWidget

from .config import ConfigManager
from .platform_utils import PlatformUI

logger = logging.getLogger(__name__)


class WindowManager:
    """Manages window creation and lifecycle."""

    def __init__(self) -> None:
        self.config = ConfigManager()
        self.active_windows: Dict[str, QWidget] = {}

    def create_window(
        self, window_class: Type[QWidget], window_id: str, *args, **kwargs
    ) -> Optional[QWidget]:
        """Create and show a new window with proper setup."""
        try:
            if window_id in self.active_windows:
                self.active_windows[window_id].raise_()
                self.active_windows[window_id].activateWindow()
                return self.active_windows[window_id]

            window = window_class(*args, **kwargs)
            PlatformUI.setup_window(window)
            self.active_windows[window_id] = window

            # Setup cleanup
            window.destroyed.connect(lambda: self.active_windows.pop(window_id, None))

            return window

        except Exception as e:
            logger.error(f"Failed to create window {window_id}: {e}")
            return None

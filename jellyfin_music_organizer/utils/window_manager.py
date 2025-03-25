"""Window management utilities."""

import logging
from typing import Any, Dict, Optional, Type, TypeVar, cast

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget

from .config import ConfigManager
from .platform_utils import PlatformUI

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=QWidget)


class WindowManager(QObject):
    """Manage window instances and their lifecycle."""

    window_created = pyqtSignal(QWidget)
    window_closed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.config = ConfigManager()
        self.active_windows: Dict[str, QWidget] = {}

    def create_window(
        self, window_class: Type[T], window_id: str, *args: Any, **kwargs: Any
    ) -> Optional[T]:
        """Create and show a new window."""
        try:
            if window_id in self.active_windows:
                window = cast(T, self.active_windows[window_id])
                window.raise_()
                window.activateWindow()
                return window

            window = window_class(*args, **kwargs)
            PlatformUI.setup_window(window)
            self.active_windows[window_id] = window

            # Connect window closure
            def on_window_closed() -> None:
                self.active_windows.pop(window_id, None)
                self.window_closed.emit(window_id)

            window.destroyed.connect(on_window_closed)
            self.window_created.emit(window)
            return window

        except Exception as e:
            logger.error(f"Failed to create window {window_id}: {e}")
            return None

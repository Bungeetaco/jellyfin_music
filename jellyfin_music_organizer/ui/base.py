import platform
from typing import Any, Dict, Optional, Union

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtWidgets import QDialog, QWidget

from ..utils.qt_types import QtConstants, WidgetAttribute, WindowFlags, WindowType
from ..utils.window_state import WindowStateManager


class DraggableWidget(QWidget):
    """Base class for draggable windows."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.drag_position: Optional[QPoint] = None
        self._setup_window()

    def _setup_window(self) -> None:
        """Set up window properties."""
        self.setWindowFlags(QtConstants.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def mousePressEvent(self, event: Optional[QMouseEvent]) -> None:
        """Handle mouse press for window dragging."""
        if event is None:
            return
        if event.button() == QtConstants.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: Optional[QMouseEvent]) -> None:
        """Handle mouse move for window dragging."""
        if event is None:
            return
        if event.buttons() & QtConstants.LeftButton and self.drag_position:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


class BaseDialog(QDialog):
    """Base class for application dialogs."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        window_title: str = "",
        icon_path: Optional[str] = None,
    ) -> None:
        super().__init__(parent)
        self.window_title = window_title
        self.icon_path = icon_path
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        if self.icon_path:
            self.setWindowIcon(QIcon(self.icon_path))
        self.setWindowTitle(self.window_title)
        self._setup_window_flags()

    def _setup_window_flags(self) -> None:
        """Set up window flags based on platform."""
        flags: Union[WindowFlags, WindowType] = (
            QtConstants.Dialog | QtConstants.WindowStaysOnTopHint
        )
        if platform.system() == "Windows":
            flags |= QtConstants.FramelessWindowHint
        self.setWindowFlags(flags)


class StatefulWidget(QWidget):
    """Base class for widgets that maintain state."""

    def __init__(self, parent: Optional[QWidget] = None, state_id: str = "") -> None:
        super().__init__(parent)
        self.state_manager = WindowStateManager(state_id or self.__class__.__name__)
        self._state: Dict[str, Any] = {}

    def save_state(self) -> None:
        """Save widget state."""
        try:
            self.state_manager.save_state(self)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def restore_state(self) -> None:
        """Restore widget state."""
        try:
            self.state_manager.restore_state(self)
        except Exception as e:
            logger.error(f"Failed to restore state: {e}")

    def closeEvent(self, event: Any) -> None:
        """Handle widget closure."""
        self.save_state()
        super().closeEvent(event)

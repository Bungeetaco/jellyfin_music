"""Qt compatibility layer for type checking."""

from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Type definitions for Qt enums and flags
QtWindowFlags = Union[Qt.WindowFlags, Qt.WindowType]
QtAlignment = Union[Qt.Alignment, Qt.AlignmentFlag]


class QtCompat:
    """Compatibility layer for Qt attributes."""

    @staticmethod
    def set_high_dpi_scaling(app: QApplication) -> None:
        """Enable high DPI scaling."""
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        except Exception:
            pass

    @staticmethod
    def get_window_flags(frameless: bool = False) -> QtWindowFlags:
        """Get appropriate window flags."""
        flags = Qt.WindowType.Window
        if frameless:
            flags |= Qt.WindowType.FramelessWindowHint
        return flags

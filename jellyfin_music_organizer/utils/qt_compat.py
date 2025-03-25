"""Qt compatibility layer for type checking."""

from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget
from .qt_types import WindowFlags, QtConstants

class QtCompat:
    """Qt compatibility utilities."""

    @staticmethod
    def set_window_flags(
        widget: QWidget,
        frameless: bool = False,
        always_on_top: bool = False,
    ) -> None:
        """Set window flags for widget."""
        flags = Qt.WindowType.Window

        if frameless:
            flags |= Qt.WindowType.FramelessWindowHint

        if always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint

        widget.setWindowFlags(flags)

    @staticmethod
    def set_widget_alignment(
        widget: QWidget,
        horizontal: Optional[Qt.AlignmentFlag] = None,
        vertical: Optional[Qt.AlignmentFlag] = None,
    ) -> None:
        """Set widget alignment."""
        alignment = Qt.AlignmentFlag(0)

        if horizontal:
            alignment |= horizontal

        if vertical:
            alignment |= vertical

        widget.setAlignment(alignment)

    @staticmethod
    def enable_high_dpi() -> None:
        """Enable high DPI scaling."""
        try:
            # Enable High DPI display with Qt6
            from PyQt6.QtGui import QGuiApplication

            QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )
            QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
            QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        except Exception:
            pass

    @staticmethod
    def get_window_flags(frameless: bool = False) -> WindowFlags:
        """Get appropriate window flags."""
        flags = QtConstants.Window
        if frameless:
            flags |= QtConstants.FramelessWindowHint
        return flags

    @staticmethod
    def setup_window(window: QWidget, frameless: bool = False) -> None:
        """Set up window flags and attributes."""
        flags = QtCompat.get_window_flags(frameless)
        window.setWindowFlags(flags)

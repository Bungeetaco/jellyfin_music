"""Qt compatibility layer for type checking."""


from PyQt5.QtWidgets import QApplication, QWidget

from .qt_types import QtConstants, WindowFlags



class QtCompat:
    """Compatibility layer for Qt attributes."""

    @staticmethod
    def set_high_dpi_scaling(app: QApplication) -> None:
        """Enable high DPI scaling."""
        app.setAttribute(QtConstants.AA_EnableHighDpiScaling)
        app.setAttribute(QtConstants.AA_UseHighDpiPixmaps)

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

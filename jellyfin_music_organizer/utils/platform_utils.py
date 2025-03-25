"""Platform-specific utilities and abstractions."""

import json
import logging
import os
import platform
import sys
from pathlib import Path
from typing import Any, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QStyleFactory, QWidget

from .qt_compat import QtCompat, QtWindowFlags

logger = logging.getLogger(__name__)


class PlatformPaths:
    """Platform-specific path handling."""

    @staticmethod
    def get_app_data_dir() -> Path:
        """Get platform-specific application data directory.

        Returns:
            Path to application data directory
        """
        system = platform.system().lower()
        if system == "windows":
            return Path(os.getenv("APPDATA", "")) / "jellyfin_music_organizer"
        elif system == "darwin":
            return Path.home() / "Library" / "Application Support" / "jellyfin_music_organizer"
        else:
            return Path.home() / ".jellyfin_music_organizer"

    @staticmethod
    def get_resource_path(resource_name: str) -> Path:
        """Get path to a resource file."""
        if hasattr(sys, "_MEIPASS"):  # PyInstaller bundle
            return Path(sys._MEIPASS) / "resources" / resource_name
        return Path(__file__).parent.parent / "resources" / resource_name


class PlatformUI:
    """Platform-specific UI adjustments."""

    @staticmethod
    def get_font_settings() -> Dict[str, Any]:
        """Get platform-specific font settings."""
        system = platform.system().lower()

        if system == "windows":
            return {"family": "Segoe UI", "size": 9}
        elif system == "darwin":
            return {"family": "SF Pro", "size": 13}
        else:  # Linux and others
            return {"family": "Ubuntu", "size": 10}

    @staticmethod
    def adjust_widget_style(widget: "QWidget") -> None:
        """Apply platform-specific widget styling."""
        system = platform.system().lower()

        if system == "darwin":
            # macOS specific adjustments
            widget.setAttribute(Qt.WA_MacShowFocusRect, False)
        elif system == "windows":
            # Windows specific adjustments
            pass
        else:
            # Linux specific adjustments
            pass

    @staticmethod
    def center_window(window: QWidget) -> None:
        """Center any window on the screen."""
        try:
            screen = QApplication.desktop().screenGeometry()
            window_size = window.geometry()
            x = (screen.width() - window_size.width()) // 2
            y = (screen.height() - window_size.height()) // 2
            window.move(x, y)
        except Exception as e:
            logger.error(f"Failed to center window: {e}")

    @staticmethod
    def setup_window(window: QWidget) -> None:
        """Configure platform-specific window settings."""
        try:
            system = platform.system()
            flags: QtWindowFlags = QtCompat.get_window_flags(frameless=(system == "Windows"))
            window.setWindowFlags(flags)

            if system == "Windows":
                window.setAttribute(Qt.WA_TranslucentBackground)
            elif system == "Darwin":
                window.setAttribute(Qt.WA_MacShowFocusRect, False)

            PlatformUI._apply_platform_style(window)
        except Exception as e:
            logger.error(f"Failed to setup window: {e}")
            window.setWindowFlags(Qt.Window)

    @staticmethod
    def _apply_platform_style(window: QWidget) -> None:
        """Apply platform-specific styling."""
        try:
            system = platform.system()
            if system == "Windows":
                window.setStyleSheet(
                    """
                    QWidget {
                        background-color: white;
                        border: 1px solid #cccccc;
                    }
                """
                )
            elif system == "Darwin":
                window.setStyleSheet(
                    """
                    QWidget {
                        background-color: rgba(255, 255, 255, 0.98);
                    }
                """
                )
            else:  # Linux
                window.setStyle(QStyleFactory.create("Fusion"))
        except Exception as e:
            logger.error(f"Failed to apply style: {e}")


class SettingsWindow(QWidget):
    def _save_settings(self) -> None:
        try:
            settings_path = PlatformPaths.get_app_data_dir() / "settings.json"
            settings_path.parent.mkdir(parents=True, exist_ok=True)

            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            raise

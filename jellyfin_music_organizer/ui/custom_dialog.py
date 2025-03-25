"""
Custom dialog window for displaying messages to the user.
"""

import json
import platform
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

# Other classes within files
from ..utils.config_manager import ConfigManager
from ..utils.notifications import NotificationManager
from ..utils.platform_utils import PlatformUI
from ..utils.qt_types import QtConstants
from ..utils.resource_manager import ResourceManager

logger = getLogger(__name__)


class CustomDialog(QDialog):
    """
    A custom dialog window for displaying messages to the user.

    This dialog:
    1. Shows a custom message in a styled window
    2. Plays a notification sound (if enabled)
    3. Can be closed with a custom close button
    """

    def __init__(self, custom_message: str, parent: Optional[QWidget] = None) -> None:
        """Initialize dialog with platform-specific settings."""
        super().__init__(parent)
        self.resource_manager = ResourceManager()
        self.config_manager = ConfigManager()
        self.settings = self.config_manager.load()
        self.notification_manager = NotificationManager()
        self.drag_position: Optional[QPoint] = None

        self.resource_manager.register(
            "notification_manager", self.notification_manager, lambda x: x.deleteLater()
        )

        self._setup_platform_specific()
        self.setup_ui(custom_message)

    def _setup_platform_specific(self) -> None:
        """Configure platform-specific window behavior."""
        system = platform.system()
        try:
            flags = QtConstants.Dialog | QtConstants.WindowStaysOnTopHint
            if system == "Darwin":
                # Use native window decorations on macOS
                self.setWindowFlags(flags)
                self.setAttribute(QtConstants.WA_MacAlwaysShowToolWindow)
            elif system == "Windows":
                # Custom window frame on Windows
                self.setWindowFlags(flags | QtConstants.FramelessWindowHint)
            else:
                # Default behavior for Linux
                self.setWindowFlags(flags)

            # Set platform-specific style
            if system == "Windows":
                self.setStyleSheet("QDialog { border: 2px solid rgba(255, 152, 152, 1); }")
            elif system == "Darwin":
                # macOS specific styling
                self.setStyleSheet("QDialog { background-color: rgba(255, 255, 255, 0.95); }")

        except Exception as e:
            logger.error(f"Failed to setup platform-specific settings: {e}")
            # Fall back to basic window flags
            self.setWindowFlags(QtConstants.Dialog)

    def center_window(self) -> None:
        """Center the dialog window on the screen."""
        PlatformUI.center_window(self)

    def showEvent(self, event: Any) -> None:
        """
        Handle the show event.

        This method:
        1. Loads settings
        2. Plays notification sound if enabled
        3. Centers the window
        """
        try:
            self.load_settings()
            if not self.settings.get("mute_sound", False):
                self.notification_manager.play_notification("default")
            super().showEvent(event)
            self.center_window()
        except Exception as e:
            logger.error(f"Show event error: {e}")

    def closeEvent(self, event: Any) -> None:
        """Handle dialog close with proper cleanup."""
        try:
            self.resource_manager.cleanup()
            super().closeEvent(event)
        except Exception as e:
            logger.error(f"Close event error: {e}")
            event.accept()

    def load_settings(self) -> Dict[str, Any]:
        """Load and validate settings from file.

        Returns:
            Dict containing settings or default values
        """
        try:
            if not Path("settings_jmo.json").exists():
                return self._get_default_settings()

            with open("settings_jmo.json", "r", encoding="utf-8") as f:
                settings = json.load(f)

            return self._validate_settings(settings)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid settings file format: {e}")
            return self._get_default_settings()
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return self._get_default_settings()

    def setup_ui(self, custom_message: str) -> None:
        """Set up the dialog UI with platform-specific styling."""
        try:
            self.setWindowTitle(f"Alert v{self.settings['version']}")
            self.setWindowIcon(QIcon(":/Octopus.ico"))

            layout = QVBoxLayout()
            self._setup_title_bar(layout)
            self._setup_message_area(layout, custom_message)
            self.setLayout(layout)

        except Exception as e:
            logger.error(f"Failed to setup dialog UI: {e}")
            raise

    def _setup_title_bar(self, layout: QVBoxLayout) -> None:
        """Set up custom title bar with platform-specific behavior."""
        try:
            if platform.system() != "Darwin":  # Skip on macOS
                title_bar = QWidget()
                title_layout = QHBoxLayout()

                icon_label = QLabel()
                icon_label.setPixmap(QIcon(":/Octopus.ico").pixmap(24, 24))
                title_layout.addWidget(icon_label)

                title_label = QLabel(f"Alert v{self.settings['version']}")
                title_layout.addWidget(title_label)
                title_layout.addStretch()

                close_button = self._create_close_button()
                title_layout.addWidget(close_button)

                title_bar.setLayout(title_layout)
                layout.addWidget(title_bar)
        except Exception as e:
            logger.error(f"Failed to setup title bar: {e}")

    def _create_close_button(self) -> QPushButton:
        """Create a close button with platform-specific styling."""
        close_button = QPushButton("X")
        close_button.setToolTip("Close window")
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: red; }"
        )
        close_button.clicked.connect(self.reject)
        return close_button

    def _setup_message_area(self, layout: QVBoxLayout, custom_message: str) -> None:
        """Set up the message area of the dialog."""
        error_label = QLabel(custom_message)
        error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(error_label)

    def mousePressEvent(self, event: Optional[QMouseEvent]) -> None:
        """Handle mouse press events for window dragging."""
        if event is None:
            return
        if event.button() == QtConstants.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def _handle_notification_error(self, error_msg: str) -> None:
        """Handle notification errors."""
        logger.warning(f"Notification error: {error_msg}")
        # Don't show error dialog for notification failures

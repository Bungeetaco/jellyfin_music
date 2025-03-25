import json
import os
import platform
from logging import getLogger
from pathlib import Path
from typing import Any, Dict

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

logger = getLogger(__name__)


class SettingsWindow(QWidget):
    """Window for managing application settings."""

    windowOpened = pyqtSignal(bool)
    windowClosed = pyqtSignal()
    settings_changed = pyqtSignal(dict)

    def __init__(self, settings: Dict[str, Any]) -> None:
        """Initialize settings window."""
        super().__init__()
        self.config_manager = ConfigManager()
        self.dialog_manager = DialogManager()
        self.settings = settings.copy()
        self._original_settings = settings.copy()
        self.version = self.settings.get("version", "unknown")
        self._setup_platform_specific()
        try:
            # Initialize attributes
            self.music_folder_path = ""
            self.destination_folder_path = ""

            # Setup and show user interface
            self.setup_ui()

            # Load settings from file if it exists
            self.load_settings()
        except Exception as e:
            logger.error(f"Failed to initialize settings window: {e}")
            raise

    def showEvent(self, event):
        self.windowOpened.emit(False)
        super().showEvent(event)
        self.center_window()

    def closeEvent(self, event: Any) -> None:
        """Handle window close with settings check."""
        try:
            if self._settings_changed():
                self.settings_changed.emit(self.settings)
            self.windowClosed.emit()
            super().closeEvent(event)
        except Exception as e:
            logger.error(f"Close event error: {e}")
            event.accept()

    def _settings_changed(self) -> bool:
        """Check if settings have been modified."""
        return any(
            self.settings.get(key) != self._original_settings.get(key) for key in self.settings
        )

    def setup_titlebar(self):
        # Hides the default titlebar
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Title bar widget
        self.title_bar = QWidget(self)
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(32)

        hbox_title_layout = QHBoxLayout(self.title_bar)
        hbox_title_layout.setContentsMargins(0, 0, 0, 0)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(":/Octopus.ico").pixmap(24, 24))
        hbox_title_layout.addWidget(self.icon_label)

        self.title_label = QLabel(f"Settings Window v{self.version}")
        self.title_label.setStyleSheet("color: white;")
        hbox_title_layout.addWidget(self.title_label)

        hbox_title_layout.addStretch()

        self.close_button = QPushButton("✕")
        self.close_button.setToolTip("Close window")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: red; }"
        )
        hbox_title_layout.addWidget(self.close_button)
        self.close_button.clicked.connect(self.close)

        hbox_title_layout.setAlignment(Qt.AlignRight)

    # Mouse events allow the title bar to be dragged around
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() <= self.title_bar.height():
            self.draggable = True
            self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if hasattr(self, "draggable") and self.draggable:
            if event.buttons() & Qt.LeftButton:
                self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = False

    def setup_ui(self) -> None:
        """Set up the settings window UI with platform-specific adjustments."""
        try:
            # Platform-specific adjustments
            is_mac = platform.system() == "Darwin"

            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(*(20,) * 4 if is_mac else (10,) * 4)

            # Title bar (skip on macOS to use native window decorations)
            if not is_mac:
                title_bar = self._create_title_bar()
                main_layout.addWidget(title_bar)

            # Folder selection section with platform-specific spacing
            folder_section = QVBoxLayout()
            folder_section.setSpacing(10 if is_mac else 5)

            # Music folder selection
            music_folder_layout = QHBoxLayout()
            self.music_folder_label = QLabel()
            self.music_folder_label.setWordWrap(True)
            music_folder_layout.addWidget(self.music_folder_label)

            select_music_btn = QPushButton("Select Music Folder")
            select_music_btn.clicked.connect(self.select_music_folder)
            music_folder_layout.addWidget(select_music_btn)

            folder_section.addLayout(music_folder_layout)
            main_layout.addLayout(folder_section)

            # Apply platform-specific window flags
            if is_mac:
                self.setWindowFlags(Qt.Window)
            else:
                self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

            self.setLayout(main_layout)

        except Exception as e:
            logger.error(f"Failed to set up settings UI: {e}")
            raise

    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def select_music_folder(self) -> None:
        """Handle music folder selection."""
        try:
            folder_path = self.dialog_manager.get_folder_dialog(
                self,
                "Select Music Folder",
                Path(self.music_folder_path) if self.music_folder_path else Path.home() / "Music",
            )

            if not folder_path:
                logger.debug("Music folder selection cancelled")
                return

            if not self._validate_folder_path(folder_path):
                logger.warning(f"Invalid music folder path: {folder_path}")
                return

            self.music_folder_path = str(folder_path)
            self.music_folder_label.setText(self.music_folder_path)
            self._save_settings()

        except Exception as e:
            logger.error(f"Failed to select music folder: {e}")
            self.show_error("Failed to select music folder")

    def _validate_folder_path(self, path: str) -> bool:
        """Validate folder path exists and is accessible.

        Args:
            path: Folder path to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            folder = Path(path)
            return folder.exists() and folder.is_dir() and os.access(folder, os.R_OK)
        except Exception as e:
            logger.error(f"Folder validation error: {e}")
            return False

    def clear_music_folder(self) -> None:
        """Clear music folder path with proper cleanup."""
        try:
            self.music_folder_path = ""
            self.music_folder_label.setText("")
            self._save_settings()
        except Exception as e:
            logger.error(f"Failed to clear music folder: {e}")

    def select_destination_folder(self) -> None:
        """Handle destination folder selection with validation."""
        try:
            destination_folder_path = QFileDialog.getExistingDirectory(
                self, "Select Destination Folder", "", QFileDialog.ShowDirsOnly
            )

            if not destination_folder_path:
                logger.debug("Destination folder selection cancelled")
                return

            if not self._validate_folder_path(destination_folder_path):
                logger.warning(f"Invalid destination folder path: {destination_folder_path}")
                return

            self.destination_folder_path = destination_folder_path
            self.destination_folder_label.setText(self.destination_folder_path)
            self._save_settings()
        except Exception as e:
            logger.error(f"Failed to select destination folder: {e}")

    def clear_destination_folder(self) -> None:
        """Clear destination folder path with proper cleanup."""
        try:
            self.destination_folder_path = ""
            self.destination_folder_label.setText("")
            self._save_settings()
        except Exception as e:
            logger.error(f"Failed to clear destination folder: {e}")

    def load_settings(self) -> None:
        """Load settings from file and update UI."""
        try:
            if not Path("settings_jmo.json").exists():
                logger.debug("No settings file found")
                return

            with open("settings_jmo.json", "r", encoding="utf-8") as f:
                settings = json.load(f)

            # Update UI with loaded settings
            self.music_folder_path = settings.get("music_folder_path", "")
            self.destination_folder_path = settings.get("destination_folder_path", "")
            self.music_folder_label.setText(self.music_folder_path)
            self.destination_folder_label.setText(self.destination_folder_path)
            self.sound_checkbox.setChecked(settings.get("mute_sound", False))
            self.illegal_chars_checkbox.setChecked(settings.get("remove_illegal_chars", True))

        except json.JSONDecodeError as e:
            logger.error(f"Invalid settings file format: {e}")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")

    def save_settings(self) -> None:
        """Save current settings to file."""
        try:
            settings = {
                "music_folder_path": self.music_folder_path,
                "destination_folder_path": self.destination_folder_path,
                "mute_sound": self.sound_checkbox.isChecked(),
                "remove_illegal_chars": self.illegal_chars_checkbox.isChecked(),
                "version": self.version,
            }

            with open("settings_jmo.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)

            logger.debug("Settings saved successfully")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            raise RuntimeError("Failed to save settings") from e

    def reset_settings(self):
        # Default settings
        self.music_folder_path = ""
        self.destination_folder_path = ""
        self.sound_checkbox.setChecked(False)
        self.illegal_chars_checkbox.setChecked(True)  # Default to True

        # Reset settings to default
        self.music_folder_label.setText(self.music_folder_path)
        self.destination_folder_label.setText(self.destination_folder_path)

        # Save settings to file
        self.save_settings()

        # Update the button text and color temporarily
        self.reset_button.setText("Success")
        self.reset_button.setStyleSheet(
            """
            background-color: rgba(255, 152, 152, 1);
            color: black;
        """
        )

        # Stop any existing reset timers before creating a new one
        if hasattr(self, "reset_reset_timer"):
            self.reset_reset_timer.stop()

        # Create a new reset timer to reset the button text and color after 1 seconds
        self.reset_reset_timer = QTimer(self)
        self.reset_reset_timer.timeout.connect(self.resetResetButton)
        self.reset_reset_timer.start(1000)

    def resetResetButton(self):
        self.reset_button.setText("Reset && Save All Settings")
        self.reset_button.setStyleSheet("")

    def _save_settings(self) -> None:
        """Save settings with validation."""
        try:
            if self._validate_settings(self.settings):
                self.config_manager.save(self.settings)
                self.settings_changed.emit(self.settings)
            else:
                logger.error("Invalid settings configuration")
                self.show_error("Invalid settings configuration")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            self.show_error(f"Failed to save settings: {str(e)}")

    def _validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate settings before saving."""
        # Implement your validation logic here
        return True  # Placeholder, actual implementation needed

    def _setup_platform_specific(self):
        # Implement platform-specific setup logic
        pass

    def show_error(self, message: str) -> None:
        # Implement error handling logic
        pass

import json
import os
from logging import getLogger
from pathlib import Path
from typing import Dict

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizeGrip,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

logger = getLogger(__name__)


class SettingsWindow(QWidget):
    """Window for managing application settings."""

    windowOpened = pyqtSignal(bool)
    windowClosed = pyqtSignal(bool)

    def __init__(self, settings: Dict[str, bool]) -> None:
        """Initialize settings window."""
        super().__init__()
        self.settings = settings
        self.version = self.settings.get("version", "unknown")
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

    def closeEvent(self, event):
        self.windowClosed.emit(True)
        super().closeEvent(event)

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
        """Set up the settings window UI."""
        try:
            # Break long line for window title
            self.setWindowTitle(f"Settings Window v{self.version}")

            # Break long line for geometry
            self.setGeometry(100, 100, 400, 300)  # x  # y  # width  # height

            # Window setup
            self.setWindowIcon(QIcon(":/Octopus.ico"))

            # Main layout
            main_layout = QVBoxLayout(self)

            # Custom title bar
            self.setup_titlebar()
            main_layout.addWidget(self.title_bar)

            # Central widget
            self.central_widget = QWidget(self)
            main_layout.addWidget(self.central_widget)

            # QVBoxLayout for central widget
            vbox_main_layout = QVBoxLayout(self.central_widget)

            # QLabel for sound
            self.sound_label = QLabel(self)
            self.sound_label.setText("Sound:")
            vbox_main_layout.addWidget(self.sound_label)

            # Create the sound checkbox
            self.sound_checkbox = QCheckBox("Mute all sound")
            self.sound_checkbox.setChecked(False)
            vbox_main_layout.addWidget(self.sound_checkbox)

            # Add a spacer item to create an empty line
            spacer_item = QSpacerItem(30, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
            vbox_main_layout.addItem(spacer_item)

            # QLabel for file handling
            self.file_handling_label = QLabel(self)
            self.file_handling_label.setText("File Handling:")
            vbox_main_layout.addWidget(self.file_handling_label)

            # Create the illegal characters checkbox
            self.illegal_chars_checkbox = QCheckBox("Remove illegal characters from filenames")
            self.illegal_chars_checkbox.setChecked(True)  # Enabled by default
            self.illegal_chars_checkbox.setToolTip(
                "Remove characters that are not allowed in filenames (e.g., :*?<>|)"
            )
            vbox_main_layout.addWidget(self.illegal_chars_checkbox)

            # Add a spacer item to create an empty line
            spacer_item = QSpacerItem(30, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
            vbox_main_layout.addItem(spacer_item)

            # QLabel for music library
            self.music_label = QLabel(self)
            self.music_label.setText("Folders:")
            vbox_main_layout.addWidget(self.music_label)

            # QHBoxLayout setup for music select and music clear
            hbox_music_clear_layout = QHBoxLayout()
            vbox_main_layout.addLayout(hbox_music_clear_layout)

            # Create music folder select button
            self.music_folder_select_button = QPushButton("Set Default Music Folder")
            hbox_music_clear_layout.addWidget(self.music_folder_select_button, 1)
            self.music_folder_select_button.clicked.connect(self.select_music_folder)

            # Create music folder clear button
            self.music_folder_clear_button = QPushButton("Clear")
            hbox_music_clear_layout.addWidget(self.music_folder_clear_button)
            self.music_folder_clear_button.clicked.connect(self.clear_music_folder)

            # Create music folder label
            self.music_folder_label = QLabel(self.music_folder_path)
            vbox_main_layout.addWidget(self.music_folder_label)

            # QHBoxLayout setup for destination select and destination clear
            hbox_destination_clear_layout = QHBoxLayout()
            vbox_main_layout.addLayout(hbox_destination_clear_layout)

            # Create destination folder select button
            self.destination_folder_select_button = QPushButton("Set Default Destination Folder")
            hbox_destination_clear_layout.addWidget(self.destination_folder_select_button, 1)
            self.destination_folder_select_button.clicked.connect(self.select_destination_folder)

            # Create destination folder clear button
            self.destination_folder_clear_button = QPushButton("Clear")
            hbox_destination_clear_layout.addWidget(self.destination_folder_clear_button)
            self.destination_folder_clear_button.clicked.connect(self.clear_destination_folder)

            # Create destination folder label
            self.destination_folder_label = QLabel(self.destination_folder_path)
            vbox_main_layout.addWidget(self.destination_folder_label)

            # Add a spacer item to create an empty line
            spacer_item = QSpacerItem(30, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
            vbox_main_layout.addItem(spacer_item)

            # QHBoxLayout setup for save and reset settings
            hbox_save_reset_layout = QHBoxLayout()
            vbox_main_layout.addLayout(hbox_save_reset_layout)

            # Create save settings button
            self.save_button = QPushButton("Save Settings")
            hbox_save_reset_layout.addWidget(self.save_button, 1)
            self.save_button.clicked.connect(self.save_settings)

            # Create a line between the save and reset button
            line_save_reset = QFrame()
            line_save_reset.setFrameShape(QFrame.VLine)
            line_save_reset.setFrameShadow(QFrame.Sunken)
            hbox_save_reset_layout.addWidget(line_save_reset)

            # Create reset settings button
            self.reset_button = QPushButton("Reset && Save All Settings")
            hbox_save_reset_layout.addWidget(self.reset_button, 1)
            self.reset_button.clicked.connect(self.reset_settings)

            # Add resizing handles
            self.bottom_right_grip = QSizeGrip(self)
            self.bottom_right_grip.setToolTip("Resize window")
            hbox_save_reset_layout.addWidget(
                self.bottom_right_grip, 0, Qt.AlignBottom | Qt.AlignRight
            )

            # Apply layout
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
        """Handle music folder selection with validation."""
        try:
            music_folder_path = QFileDialog.getExistingDirectory(
                self, "Select Music Folder", "", QFileDialog.ShowDirsOnly
            )
            if not music_folder_path:
                logger.debug("Music folder selection cancelled")
                return

            if not self._validate_folder_path(music_folder_path):
                logger.warning(f"Invalid music folder path: {music_folder_path}")
                return

            self.music_folder_path = music_folder_path
            self.music_folder_label.setText(self.music_folder_path)
            self._save_settings()
        except Exception as e:
            logger.error(f"Failed to select music folder: {e}")

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

    def save_settings(self):
        # Create settings dictionary
        settings = {
            "music_folder_path": self.music_folder_path,
            "destination_folder_path": self.destination_folder_path,
            "mute_sound": self.sound_checkbox.isChecked(),
            "remove_illegal_chars": self.illegal_chars_checkbox.isChecked(),
        }

        # Save settings to file
        with open("settings_jmo.json", "w") as file:
            json.dump(settings, file, indent=4)

        # Update the button text and color temporarily
        self.save_button.setText("Success")
        self.save_button.setStyleSheet(
            """
            background-color: rgba(255, 152, 152, 1);
            color: black;
        """
        )

        # Stop any existing save timers before creating a new one
        if hasattr(self, "reset_save_timer"):
            self.reset_save_timer.stop()

        # Create a new save timer to reset the button text and color after 1 seconds
        self.reset_save_timer = QTimer(self)
        self.reset_save_timer.timeout.connect(self.resetSaveButton)
        self.reset_save_timer.start(1000)

    def resetSaveButton(self):
        self.save_button.setText("Save Settings")
        self.save_button.setStyleSheet("")

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

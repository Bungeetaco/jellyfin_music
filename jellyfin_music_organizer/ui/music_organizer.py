"""
Main window for the Jellyfin Music Organizer application.
"""

import json
import platform
from logging import getLogger
from typing import Any, Dict, List

from PyQt5.QtCore import QFont, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizeGrip,
    QSizePolicy,
    QSpacerItem,
    QStyleFactory,
    QVBoxLayout,
    QWidget,
)

# Other classes within files
from ..core.organize_thread import OrganizeThread
from ..utils.config import ConfigManager
from ..utils.notifications import NotificationManager
from ..utils.platform_utils import PlatformUI
from ..utils.window_manager import WindowManager
from .custom_dialog import CustomDialog
from .music_error_window import MusicErrorWindow
from .replace_skip_window import ReplaceSkipWindow
from .settings_window import SettingsWindow

logger = getLogger(__name__)


class MusicOrganizer(QWidget):
    """
    Main window for the Jellyfin Music Organizer application.

    This window:
    1. Provides the main user interface
    2. Handles folder selection
    3. Manages the organization process
    4. Shows progress and results
    """

    def __init__(self) -> None:
        """Initialize the MusicOrganizer window."""
        super().__init__()
        self.window_manager = WindowManager()
        self.notification_manager = NotificationManager()
        self.config_manager = ConfigManager()
        self.settings = self.config_manager.load()
        self._setup_platform_specific()

        # Version Control
        self.version: str = "3.06"

        # Set default settings
        self.music_folder_path: str = ""
        self.destination_folder_path: str = ""

        # Setup and show user interface
        self.setup_ui()

        # Load settings from file if it exists
        self.load_settings()

        # Show starting window
        self.show()

    def showEvent(self, event: Any) -> None:
        """
        Handle the show event.

        This method centers the window on the screen.
        """
        super().showEvent(event)
        self.center_window()

    def setup_titlebar(self) -> None:
        """
        Set up the custom title bar.

        This method:
        1. Creates a custom title bar widget
        2. Adds window controls (minimize, close)
        3. Makes the window draggable
        """
        # Hides the default titlebar
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Title bar widget
        self.title_bar: QWidget = QWidget(self)
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(32)

        hbox_title_layout: QHBoxLayout = QHBoxLayout(self.title_bar)
        hbox_title_layout.setContentsMargins(0, 0, 0, 0)

        self.icon_label: QLabel = QLabel()
        self.icon_label.setPixmap(QIcon(":/Octopus.ico").pixmap(24, 24))
        hbox_title_layout.addWidget(self.icon_label)

        self.title_label: QLabel = QLabel(f"Music Organizer v{self.version}")
        self.title_label.setStyleSheet("color: white;")
        hbox_title_layout.addWidget(self.title_label)

        hbox_title_layout.addStretch()

        self.settings_button: QPushButton = QPushButton("⚙")
        self.settings_button.setToolTip("Settings")
        self.settings_button.setFixedSize(24, 24)
        self.settings_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: blue; }"
        )
        hbox_title_layout.addWidget(self.settings_button)
        self.settings_button.clicked.connect(self.settings_window)

        self.minimize_button: QPushButton = QPushButton("—")
        self.minimize_button.setToolTip("Minimize window")
        self.minimize_button.setFixedSize(24, 24)
        self.minimize_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: green; }"
        )
        hbox_title_layout.addWidget(self.minimize_button)
        self.minimize_button.clicked.connect(self.showMinimized)

        self.close_button: QPushButton = QPushButton("✕")
        self.close_button.setToolTip("Close window")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: red; }"
        )
        hbox_title_layout.addWidget(self.close_button)
        self.close_button.clicked.connect(self.close)

        hbox_title_layout.setAlignment(Qt.AlignRight)

    def mousePressEvent(self, event: Any) -> None:
        """
        Handle mouse press events.

        This method enables window dragging when clicking the title bar.
        """
        if event.button() == Qt.LeftButton and event.y() <= self.title_bar.height():
            self.draggable = True
            self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event: Any) -> None:
        """
        Handle mouse move events.

        This method moves the window when dragging.
        """
        if hasattr(self, "draggable") and self.draggable:
            if event.buttons() & Qt.LeftButton:
                self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event: Any) -> None:
        """
        Handle mouse release events.

        This method disables window dragging.
        """
        if event.button() == Qt.LeftButton:
            self.draggable = False

    def setup_ui(self) -> None:
        """
        Set up the main user interface.

        This method:
        1. Creates the window layout
        2. Adds folder selection buttons
        3. Sets up the progress bar
        4. Adds window controls
        """
        # Window setup
        self.setWindowTitle(f"Music Organizer v{self.version}")
        self.setWindowIcon(QIcon(":/Octopus.ico"))
        self.setGeometry(100, 100, 400, 260)  # Set initial size of window (x, y, width, height)

        # Main layout
        main_layout: QVBoxLayout = QVBoxLayout(self)

        # Custom title bar
        self.setup_titlebar()
        main_layout.addWidget(self.title_bar)

        # Central widget
        self.central_widget: QWidget = QWidget(self)
        main_layout.addWidget(self.central_widget)

        # QVBoxLayout for central widget
        vbox_main_layout: QVBoxLayout = QVBoxLayout(self.central_widget)

        # Create music folder select button
        self.music_folder_select_button: QPushButton = QPushButton("Select Music Folder")
        vbox_main_layout.addWidget(self.music_folder_select_button)
        self.music_folder_select_button.clicked.connect(self.select_music_folder)

        # Create music folder label
        self.music_folder_label: QLabel = QLabel(self.music_folder_path)
        vbox_main_layout.addWidget(self.music_folder_label)

        # Create destination folder select button
        self.destination_folder_select_button: QPushButton = QPushButton(
            "Select Destination Folder"
        )
        vbox_main_layout.addWidget(self.destination_folder_select_button)
        self.destination_folder_select_button.clicked.connect(self.select_destination_folder)

        # Create destination folder label
        self.destination_folder_label: QLabel = QLabel(self.destination_folder_path)
        vbox_main_layout.addWidget(self.destination_folder_label)

        # Add a spacer item to create an empty line
        spacer_item: QSpacerItem = QSpacerItem(30, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        vbox_main_layout.addItem(spacer_item)

        # Create organize button
        self.organize_button: QPushButton = QPushButton("Organize")
        # Check if settings are empty
        if not self.music_folder_path or not self.destination_folder_path:
            self.organize_button.setEnabled(False)
        else:
            self.organize_button.setEnabled(True)
        vbox_main_layout.addWidget(self.organize_button)
        self.organize_button.clicked.connect(self.organize_function)

        # Create label for number of songs
        self.number_songs_label: QLabel = QLabel("")
        vbox_main_layout.addWidget(self.number_songs_label)

        # QHBoxLayout setup for progress bar and grip
        hbox_progress_grip_layout: QHBoxLayout = QHBoxLayout()
        vbox_main_layout.addLayout(hbox_progress_grip_layout)

        # Create progress bar
        self.music_progress_bar: QProgressBar = QProgressBar()
        self.music_progress_bar.setValue(0)
        self.music_progress_bar.setMaximum(100)
        hbox_progress_grip_layout.addWidget(self.music_progress_bar)

        # Add resizing handles
        self.bottom_right_grip: QSizeGrip = QSizeGrip(self)
        self.bottom_right_grip.setToolTip("Resize window")
        hbox_progress_grip_layout.addWidget(
            self.bottom_right_grip, 0, Qt.AlignBottom | Qt.AlignRight
        )

    def center_window(self) -> None:
        """Center the window on the screen."""
        PlatformUI.center_window(self)

    def select_music_folder(self) -> None:
        """
        Open a dialog to select the music source folder.

        This method:
        1. Shows a folder selection dialog
        2. Updates the UI with the selected path
        3. Resets progress indicators
        """
        music_folder_path = QFileDialog.getExistingDirectory(self, "Select Music Folder")
        if music_folder_path:
            self.music_folder_path = music_folder_path
            self.music_folder_label.setText(self.music_folder_path)
            # Check if settings are empty
            if not self.music_folder_path or not self.destination_folder_path:
                self.organize_button.setEnabled(False)
            else:
                self.organize_button.setEnabled(True)
            self.reset_progress_songs_label()

    def select_destination_folder(self) -> None:
        """
        Open a dialog to select the destination folder.

        This method:
        1. Shows a folder selection dialog
        2. Updates the UI with the selected path
        3. Resets progress indicators
        """
        destination_folder_path = QFileDialog.getExistingDirectory(
            self, "Select Destination Folder"
        )
        if destination_folder_path:
            self.destination_folder_path = destination_folder_path
            self.destination_folder_label.setText(self.destination_folder_path)
            # Check if settings are empty
            if not self.music_folder_path or not self.destination_folder_path:
                self.organize_button.setEnabled(False)
            else:
                self.organize_button.setEnabled(True)
            self.reset_progress_songs_label()

    def reset_progress_songs_label(self) -> None:
        """Reset the progress bar and songs label to their initial state."""
        self.music_progress_bar.setValue(0)  # Reset the progress bar to 0
        self.music_progress_bar.setStyleSheet("")  # Reset the style sheet to default
        self.number_songs_label.setText("")  # Reset number of songs label

    def load_settings(self) -> None:
        """
        Load settings from the settings file.

        This method:
        1. Reads the settings file
        2. Updates the UI with saved paths
        3. Updates the organize button state
        """
        try:
            with open("settings_jmo.json", "r") as f:
                self.settings: Dict[str, Any] = json.load(f)
                self.music_folder_path = self.settings.get("music_folder_path", "")
                self.destination_folder_path = self.settings.get("destination_folder_path", "")

                # Update the labels with the loaded values
                self.music_folder_label.setText(self.music_folder_path)
                self.destination_folder_label.setText(self.destination_folder_path)

                # Check if settings are empty
                if not self.music_folder_path or not self.destination_folder_path:
                    self.organize_button.setEnabled(False)
                else:
                    self.organize_button.setEnabled(True)
        except FileNotFoundError:
            # Initialize self.settings dictionary
            self.settings = {}

    def organize_function(self) -> None:
        """
        Start the music organization process.

        This method:
        1. Disables UI elements
        2. Creates and starts the organization thread
        3. Connects signals for progress updates
        """
        # Disable UI elements
        self.user_interface(False)
        # Variables needed in OrganizeThread
        info: Dict[str, str] = {
            "selected_music_folder_path": self.music_folder_path,
            "selected_destination_folder_path": self.destination_folder_path,
        }
        self.organize_thread = OrganizeThread(info)
        self.organize_thread.number_songs_signal.connect(self.number_songs)
        self.organize_thread.music_progress_signal.connect(self.music_progress)
        self.organize_thread.kill_thread_signal.connect(self.kill_thread)
        self.organize_thread.custom_dialog_signal.connect(self.custom_dialog_function)
        self.organize_thread.organize_finish_signal.connect(self.organize_finish)
        self.organize_thread.start()

    def user_interface(self, msg: bool) -> None:
        """
        Enable or disable UI elements.

        Args:
            msg: True to enable UI elements, False to disable them
        """
        # Define a list of UI elements to enable/disable
        ui_elements: List[QWidget] = [
            self.destination_folder_select_button,
            self.music_folder_select_button,
            self.organize_button,
            self.close_button,
            self.settings_button,
        ]

        # Set the enabled state of each element based on the value of msg
        enabled = msg
        for element in ui_elements:
            element.setEnabled(enabled)

    def number_songs(self, msg: int) -> None:
        """
        Update the number of songs label.

        Args:
            msg: Number of songs found
        """
        self.number_songs_label.setText(f"Number of songs found: {msg}")
        if msg:
            # Initialize progress bar at zero percent
            self.music_progress(0)

    def music_progress(self, msg: int) -> None:
        """
        Update the progress bar.

        Args:
            msg: Current progress percentage
        """
        self.music_progress_bar.setValue(int(msg))
        if self.music_progress_bar.value() == self.music_progress_bar.maximum():
            # Update the style sheet for the progress bar
            self.music_progress_bar.setStyleSheet(
                """
                QProgressBar {
                    border: 1px solid black;
                    text-align: center;
                    color: black;
                    background-color: rgba(255, 152, 152, 1);
                }

                QProgressBar::chunk {
                    background-color: rgba(255, 152, 152, 1);
                }
            """
            )
        else:
            # Check if the current style sheet is different from an empty string
            if self.music_progress_bar.styleSheet() != "":
                # Reset the style sheet to default
                self.music_progress_bar.setStyleSheet("")

    def kill_thread(self, msg: str) -> None:
        """
        Clean up threads.

        Args:
            msg: Type of thread to kill ('organize' or 'notification')
        """
        if msg == "organize" and hasattr(self, "organize_thread"):
            # Delete OrganizeThread if it exists
            del self.organize_thread
            # Re-enable UI elements
            self.user_interface(True)
        if msg == "notification" and hasattr(self, "notification_thread"):
            # Delete NotificationAudioThread if it exists
            del self.notification_thread

    def custom_dialog_function(self, msg: str) -> None:
        """
        Show a custom dialog with a message.

        Args:
            msg: Message to display in the dialog
        """
        if msg:
            # No songs were found
            custom_dialog = CustomDialog(msg)
            custom_dialog.exec_()

    def organize_finish(self, recall_files: Dict[str, List[Dict[str, Any]]]) -> None:
        """Handle completion of the organization process."""
        try:
            self.kill_thread("organize")
            self.recall_files = recall_files

            if recall_files["replace_skip_files"]:
                if not self.settings.get("mute_sound", False):
                    self.notification_manager.play_notification("alert")
                self.organize_replace_skip()
            else:
                self.replace_skip_finish()
        except Exception as e:
            logger.error(f"Organization completion failed: {e}")
            self.custom_dialog_function("Failed to complete organization")

    def organize_replace_skip(self) -> None:
        """Show the replace/skip window for files that already exist."""
        if self.recall_files["replace_skip_files"]:
            # Music File Replace Skip Window
            self.music_replace_skip_window = ReplaceSkipWindow(
                self.recall_files["replace_skip_files"]
            )
            self.music_replace_skip_window.windowClosed.connect(self.replace_skip_finish)
            self.music_replace_skip_window.windowOpened.connect(self.user_interface)
            self.music_replace_skip_window.show()

    def replace_skip_finish(self) -> None:
        """Handle completion of replace/skip process."""
        try:
            self.user_interface(True)
            self.music_progress(self.music_progress_bar.maximum())

            if self.recall_files["error_files"]:
                if not self.settings.get("mute_sound", False):
                    self.notification_manager.play_notification("error")
                self.organize_error()
            else:
                if not self.settings.get("mute_sound", False):
                    self.notification_manager.play_notification("complete")
        except Exception as e:
            logger.error(f"Replace/skip completion failed: {e}")
            self.custom_dialog_function("Failed to complete file processing")

    def organize_error(self) -> None:
        """Show the error window for files with errors."""
        try:
            if not hasattr(self, "recall_files") or not self.recall_files.get("error_files"):
                logger.warning("No error files to display")
                return

            error_window = self.window_manager.create_window(
                MusicErrorWindow, "error_window", self.recall_files["error_files"]
            )
            if error_window:
                error_window.windowClosed.connect(self.user_interface)
                error_window.windowOpened.connect(self.user_interface)
                error_window.custom_dialog_signal.connect(self.custom_dialog_function)
                error_window.show()

        except Exception as e:
            logger.error(f"Failed to show error window: {e}")
            self.custom_dialog_function("Failed to display error window")

    def settings_window(self) -> None:
        """Show the settings window."""
        try:
            settings_data = self.get_current_settings()
            settings_window = self.window_manager.create_window(
                SettingsWindow, "settings_window", settings_data
            )
            if settings_window:
                settings_window.windowClosed.connect(self.settings_finish)
                settings_window.windowOpened.connect(self.user_interface)
                settings_window.show()

        except Exception as e:
            logger.error(f"Failed to show settings window: {e}")
            self.custom_dialog_function("Failed to open settings")

    def settings_finish(self) -> None:
        """Handle completion of settings changes."""
        try:
            self.user_interface(True)
            self.load_settings()
            self.reset_progress_songs_label()
        except Exception as e:
            logger.error(f"Failed to finish settings update: {e}")
            self.custom_dialog_function("Failed to apply settings changes")

    def _setup_platform_specific(self) -> None:
        """Configure platform-specific window behavior."""
        try:
            system = platform.system()
            if system == "Windows":
                self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
                QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
            elif system == "Darwin":
                self.setWindowFlags(Qt.Window)
                self.setAttribute(Qt.WA_MacShowFocusRect, False)
            else:  # Linux
                self.setWindowFlags(Qt.Window)
                self.setStyle(QStyleFactory.create("Fusion"))
        except Exception as e:
            logger.error(f"Failed to setup platform-specific window: {e}")
            self.setWindowFlags(Qt.Window)  # Fallback

        # Apply platform-specific font settings
        font_settings = PlatformUI.get_font_settings()
        self.setFont(QFont(font_settings["family"], font_settings["size"]))

"""
Custom dialog window for displaying messages to the user.
"""

from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
                            QPushButton, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import json
from ..resources import resources_rc

# Other classes within files
from ..core.notification_audio_thread import NotificationAudioThread

class CustomDialog(QDialog):
    """
    A custom dialog window for displaying messages to the user.
    
    This dialog:
    1. Shows a custom message in a styled window
    2. Plays a notification sound (if enabled)
    3. Can be closed with a custom close button
    """
    
    def __init__(self, custom_message: str) -> None:
        """
        Initialize the CustomDialog.
        
        Args:
            custom_message: The message to display in the dialog
        """
        super().__init__()

        # Version Control
        self.version: str = '3.06'

        # Set notification thread variable
        self.notification_thread: Optional[NotificationAudioThread] = None

        # Hides the default titlebar
        self.setWindowFlag(Qt.FramelessWindowHint)

        # Window title, icon, and size
        self.setWindowTitle(f'Alert v{self.version}')
        self.setWindowIcon(QIcon(':/Octopus.ico'))

        # Main layout
        layout: QVBoxLayout = QVBoxLayout()

        # Custom title bar widget
        title_bar_widget: QWidget = QWidget()
        layout.addWidget(title_bar_widget)

        # Title bar layout
        title_layout: QHBoxLayout = QHBoxLayout()

        # Icon top left
        icon_label: QLabel = QLabel()
        icon_label.setPixmap(QIcon(':/Octopus.ico').pixmap(24, 24))
        title_layout.addWidget(icon_label)

        title_label: QLabel = QLabel(f"Alert v{self.version}")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        close_button: QPushButton = QPushButton("X")
        close_button.setToolTip('Close window')
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet(
            "QPushButton { color: white; background-color: transparent; }"
            "QPushButton:hover { background-color: red; }"
        )
        title_layout.addWidget(close_button)
        close_button.clicked.connect(self.reject)

        title_bar_widget.setLayout(title_layout)

        # Error message label
        error_label: QLabel = QLabel(custom_message)
        error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(error_label)
        self.setLayout(layout)

        # Apply stylesheet for red border
        self.setStyleSheet("QDialog { border: 2px solid rgba(255, 152, 152, 1); }")

    def center_window(self) -> None:
        """Center the dialog window on the screen."""
        screen = QApplication.desktop().screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def showEvent(self, event: Any) -> None:
        """
        Handle the show event.
        
        This method:
        1. Loads settings
        2. Plays notification sound if enabled
        3. Centers the window
        """
        # Load settings from file if it exists
        self.load_settings()
        if not self.settings.get('mute_sound', False):
            self.notification_thread = NotificationAudioThread('audio_ding') # (name of file)
            self.notification_thread.start()
        super().showEvent(event)
        self.center_window()

    def closeEvent(self, event: Any) -> None:
        """
        Handle the close event.
        
        This method:
        1. Stops the notification sound
        2. Waits for the thread to finish
        """
        if self.notification_thread and self.notification_thread.isRunning():
            self.notification_thread.terminate()
        super().closeEvent(event)
        # Wait for the thread to finish before quitting the application
        if self.notification_thread:
            self.notification_thread.wait()
        
    def load_settings(self) -> None:
        """Load settings from the settings file."""
        try:
            with open('settings_jmo.json', 'r') as f:
                self.settings: Dict[str, Any] = json.load(f)

        except FileNotFoundError:
            # Initialize self.settings dictionary
            self.settings = {}
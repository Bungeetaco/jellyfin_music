import shutil
from logging import getLogger
from pathlib import Path
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCloseEvent, QIcon, QMouseEvent, QShowEvent
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QSizeGrip,
    QVBoxLayout,
    QWidget,
)

from ..utils.qt_types import QtConstants

logger = getLogger(__name__)


class ReplaceSkipWindow(QWidget):
    """Window for handling file replace/skip decisions."""

    windowOpened = pyqtSignal(bool)
    windowClosed = pyqtSignal()

    def __init__(self, replace_skip_files: List[Dict[str, str]]) -> None:
        """Initialize the replace/skip window."""
        super().__init__()

        # Version Control
        self.version = "3.06"

        self.replace_skip_files = replace_skip_files
        self.total_entries = len(self.replace_skip_files)

        # Setup and show user interface
        self.setup_ui()

    def showEvent(self, event: QShowEvent) -> None:
        """Handle show event.

        Args:
            event: Show event from Qt
        """
        self.windowOpened.emit(False)
        super().showEvent(event)
        self.center_window()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle close event.

        Args:
            event: Close event from Qt
        """
        self.windowClosed.emit()
        super().closeEvent(event)

    def setup_titlebar(self) -> None:
        """Set up the custom titlebar."""
        # Hides the default titlebar
        self.setWindowFlag(QtConstants.FramelessWindowHint)

        # Title bar widget
        self.title_bar = QWidget(self)
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(32)

        hbox_title_layout = QHBoxLayout(self.title_bar)
        hbox_title_layout.setContentsMargins(0, 0, 0, 0)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(":/Octopus.ico").pixmap(24, 24))
        hbox_title_layout.addWidget(self.icon_label)

        self.title_label = QLabel(f"Replace or Skip Files Window v{self.version}")
        self.title_label.setStyleSheet("color: white;")
        hbox_title_layout.addWidget(self.title_label)

        hbox_title_layout.addStretch()

    # Mouse events allow the title bar to be dragged around
    def mousePressEvent(self, event: Optional[QMouseEvent]) -> None:
        """Handle mouse press event."""
        if event is None:
            return
        if event.button() == Qt.MouseButton.LeftButton and event.y() <= self.title_bar.height():
            self.draggable = True
            self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event: Optional[QMouseEvent]) -> None:
        """Handle mouse move event."""
        if event is None:
            return
        if hasattr(self, "draggable") and self.draggable:
            if event.buttons() & Qt.MouseButton.LeftButton:
                self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event: Optional[QMouseEvent]) -> None:
        """Handle mouse release event."""
        if event is None:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.draggable = False

    def setup_ui(self) -> None:
        """Set up the user interface."""
        # Window setup
        self.setWindowTitle(f"Replace or Skip Files Window v{self.version}")
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

        # QLabel setup
        self.label = QLabel()
        vbox_main_layout.addWidget(self.label)

        # QListWidget setup
        self.list_widget = QListWidget()
        vbox_main_layout.addWidget(self.list_widget)

        # QHBoxLayout setup for buttons
        hbox_button_layout = QHBoxLayout()
        vbox_main_layout.addLayout(hbox_button_layout)

        # "Skip File" button setup
        self.skip_file_button = QPushButton("Skip File")
        hbox_button_layout.addWidget(self.skip_file_button)
        self.skip_file_button.clicked.connect(self.skip_file)

        # "Skip All" button setup
        self.skip_all_button = QPushButton("Skip All")
        hbox_button_layout.addWidget(self.skip_all_button)
        self.skip_all_button.clicked.connect(self.skip_all)

        # "Replace File" button setup
        self.replace_file_button = QPushButton("Replace File")
        hbox_button_layout.addWidget(self.replace_file_button)
        self.replace_file_button.clicked.connect(self.replace_file)

        # "Replace All" button setup
        self.replace_all_button = QPushButton("Replace All")
        hbox_button_layout.addWidget(self.replace_all_button)
        self.replace_all_button.clicked.connect(self.replace_all)

        # QHBoxLayout setup for progress bar and grip
        hbox_progress_grip_layout = QHBoxLayout()
        vbox_main_layout.addLayout(hbox_progress_grip_layout)

        # Create progress bar
        self.music_progress_bar = QProgressBar()
        self.music_progress_bar.setValue(0)
        self.music_progress_bar.setMaximum(100)
        hbox_progress_grip_layout.addWidget(self.music_progress_bar)

        # Add resizing handles
        self.bottom_right_grip = QSizeGrip(self)
        self.bottom_right_grip.setToolTip("Resize window")
        hbox_progress_grip_layout.addWidget(
            self.bottom_right_grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight
        )

        # Populate QListWidget
        self.populate_list_widget()

        # Connect signal for item selection change in QListWidget
        self.list_widget.itemSelectionChanged.connect(self.update_label)

        # Update the label initially
        self.update_label()

    def center_window(self) -> None:
        """Center the window on the screen."""
        desktop = QApplication.desktop()
        if desktop is None:
            logger.warning("Could not get desktop widget")
            return

        screen = desktop.screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def populate_list_widget(self) -> None:
        """Populate the list widget with file entries."""
        for entry in self.replace_skip_files:
            self.list_widget.addItem(entry["file_name"])
        self.list_widget.setCurrentRow(0)

    def update_label(self) -> None:
        """Update the information label with current file details."""
        try:
            selected_item = self.list_widget.currentItem()
            if selected_item:
                selected_file = selected_item.text()
                selected_entry = next(
                    (
                        entry
                        for entry in self.replace_skip_files
                        if entry["file_name"] == selected_file
                    ),
                    None,
                )
                if selected_entry:
                    message = (
                        f"The destination:\n"
                        f"{selected_entry['new_location']}\n"
                        f"Already has a file named:\n"
                        f"{selected_entry['file_name']}"
                    )
                    self.label.setText(message)
        except Exception as e:
            logger.error(f"Failed to update label: {e}")

    def skip_file(self) -> None:
        """Handle skipping the current file."""
        current_item = self.list_widget.currentItem()
        if current_item is None:
            logger.warning("No item selected")
            return

        selected_file = current_item.text()
        selected_entry = next(
            (entry for entry in self.replace_skip_files if entry["file_name"] == selected_file),
            None,
        )
        if selected_entry:
            self.replace_skip_files.remove(selected_entry)
            self.list_widget.takeItem(self.list_widget.currentRow())
            self.update_label()

        remaining_entries = self.list_widget.count()
        if remaining_entries > 0:
            progress_value = int((1 - (remaining_entries / self.total_entries)) * 100)
        else:
            progress_value = self.music_progress_bar.maximum()
        self.music_progress_bar.setValue(progress_value)

        if remaining_entries == 0:
            self.close()

    def skip_all(self) -> None:
        """Skip all remaining files."""
        self.replace_skip_files.clear()
        self.list_widget.clear()
        self.label.clear()
        self.music_progress_bar.setValue(self.music_progress_bar.maximum())
        self.close()

    def replace_file(self) -> None:
        """Handle replacing the current file."""
        current_item = self.list_widget.currentItem()
        if current_item is None:
            logger.warning("No item selected")
            return

        selected_file = current_item.text()
        selected_entry = next(
            (entry for entry in self.replace_skip_files if entry["file_name"] == selected_file),
            None,
        )
        if selected_entry:
            self.replace_file_action(selected_entry)
            self.skip_file()

    def replace_all(self) -> None:
        """Replace all remaining files."""
        while self.list_widget.count() > 0:
            current_item = self.list_widget.item(0)
            if current_item is None:
                continue

            selected_file = current_item.text()
            selected_entry = next(
                (entry for entry in self.replace_skip_files if entry["file_name"] == selected_file),
                None,
            )
            if selected_entry:
                self.replace_file_action(selected_entry)
                self.skip_file()

    def replace_file_action(self, entry: Dict[str, str]) -> None:
        """Perform the file replacement action."""
        new_location = entry["new_location"]
        file_name = entry["file_name"]
        path_in_str = entry["path_in_str"]

        Path(new_location).mkdir(parents=True, exist_ok=True)
        shutil.copy(path_in_str, f"{new_location}/{file_name}")

    def update_file_info(self, source_path: str, destination_path: str, file_exists: bool) -> None:
        """Update the window with information about the current file operation."""
        self.source_path = source_path
        self.destination_path = destination_path
        self.file_exists = file_exists

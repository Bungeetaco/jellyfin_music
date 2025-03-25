import csv
import json
import os
import platform
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, List, Union, Callable
from typing_extensions import TypeAlias

import openpyxl
from PyQt5.QtCore import QSettings, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSizeGrip,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..utils.dialogs import DialogManager
from ..utils.notifications import NotificationManager
from ..utils.platform_utils import PlatformUI
from ..utils.window_state import WindowStateManager
from ..utils.qt_types import QtConstants

logger = getLogger(__name__)

# Type definitions
ErrorDict: TypeAlias = Dict[str, Union[str, List[str], Dict[str, str]]]


class MusicErrorWindow(QWidget):
    """Widget for displaying and managing music file errors."""

    windowOpened = pyqtSignal(bool)
    windowClosed = pyqtSignal(bool)
    custom_dialog_signal = pyqtSignal(str)
    reset_copy_timer: QTimer

    def __init__(self, error_files: List[ErrorDict]) -> None:
        """Initialize the error window.

        Args:
            error_files: List of dictionaries containing error information.
        """
        super().__init__()
        self.window_state = WindowStateManager("MusicErrorWindow")
        self.notification_manager = NotificationManager()

        if not self._validate_error_files(error_files):
            raise ValueError("Invalid error files format")

        self.error_files = error_files
        self._setup_platform_specific()
        self.setup_ui()

        if not self.window_state.restore_state(self):
            PlatformUI.center_window(self)

    def showEvent(self, event: Any) -> None:
        """Handle window show event."""
        try:
            self.windowOpened.emit(False)
            super().showEvent(event)
            self.center_window()
        except Exception as e:
            logger.error(f"Show event error: {e}")

    def closeEvent(self, event: Any) -> None:
        """Handle window close with state saving."""
        try:
            self.window_state.save_state(self)
            super().closeEvent(event)
        except Exception as e:
            logger.error(f"Close event error: {e}")
            event.accept()

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

        self.title_label = QLabel(f"Music Error Window v{self.version}")
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
    def mousePressEvent(self, event: Any) -> None:
        """Handle mouse press event for window dragging."""
        if event.button() == Qt.LeftButton and event.y() <= self.title_bar.height():
            self.draggable = True
            self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event: Any) -> None:
        """Handle mouse move event for window dragging."""
        if hasattr(self, "draggable") and self.draggable:
            if event.buttons() & Qt.LeftButton:
                self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event: Any) -> None:
        """Handle mouse release event for window dragging."""
        if event.button() == Qt.LeftButton:
            self.draggable = False

    def setup_ui(self) -> None:
        """Set up the user interface."""
        try:
            # Window title, icon, and size
            self.setWindowTitle(f"Music Error Window v{self.version}")
            self.setWindowIcon(QIcon(":/Octopus.ico"))

            # Main layout
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better appearance

            # Custom title bar
            self.setup_titlebar()
            main_layout.addWidget(self.title_bar)

            # Central widget
            self.central_widget = QWidget(self)
            main_layout.addWidget(self.central_widget)

            # QVBoxLayout for central widget
            vbox_main_layout = QVBoxLayout(self.central_widget)

            # QHBoxLayout setup for file list and test box
            hbox_list_text_layout = QHBoxLayout()
            vbox_main_layout.addLayout(hbox_list_text_layout)

            # Create the file list widget on the top
            self.file_list_widget = QListWidget(self)
            hbox_list_text_layout.addWidget(self.file_list_widget)
            self.file_list_widget.currentItemChanged.connect(self.displayDetails)

            # QLabel for text details
            text_label = QLabel(self)
            text_label.setText(
                "Files that don't have any metadata are unreadable by mutagen\n\n"
                "These are the known audio file keys that are being looked for:\n"
                "(capitalization doesn't matter)\n"
                "artist_values = ['©art', 'artist', 'author', 'tpe1']\n"
                "album_values = ['©alb', 'album', 'talb', 'wm/albumtitle']\n\n"
                "These audio files have missing artist and/or album keys\n"
                "Either:\n"
                "- Your files don't have an artist/album name\n"
                "- New keys need to be added to the program\n"
                "- Your file is corrupt/tampered with"
            )
            hbox_list_text_layout.addWidget(text_label)

            # Create the details display widget on the bottom
            self.details_display = QTextEdit(self)
            self.details_display.setReadOnly(True)
            self.details_display.setLineWrapMode(QTextEdit.NoWrap)
            vbox_main_layout.addWidget(self.details_display)

            # QHBoxLayout setup for buttons and grip
            hbox_buttons_grip_layout = QHBoxLayout()
            vbox_main_layout.addLayout(hbox_buttons_grip_layout)

            # Create the copy button
            self.copy_button = QPushButton("Copy Bottom")
            self.copy_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            hbox_buttons_grip_layout.addWidget(self.copy_button)
            self.copy_button.clicked.connect(self.copyDetails)

            # Create the CSV button
            self.txt_button = QPushButton("Generate TXT File")
            self.txt_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            hbox_buttons_grip_layout.addWidget(self.txt_button)
            self.txt_button.clicked.connect(self.generateTXT)

            # Create the CSV button
            self.csv_button = QPushButton("Generate CSV File")
            self.csv_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            hbox_buttons_grip_layout.addWidget(self.csv_button)
            self.csv_button.clicked.connect(self.generateCSV)

            # Create the Excel button
            self.excel_button = QPushButton("Generate Excel File")
            self.excel_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            hbox_buttons_grip_layout.addWidget(self.excel_button)
            self.excel_button.clicked.connect(self.generateExcel)

            # Create the JSON button
            self.json_button = QPushButton("Generate JSON File")
            self.json_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            hbox_buttons_grip_layout.addWidget(self.json_button)
            self.json_button.clicked.connect(self.generateJSON)

            # Add resizing handles
            self.bottom_right_grip = QSizeGrip(self)
            self.bottom_right_grip.setToolTip("Resize window")
            hbox_buttons_grip_layout.addWidget(
                self.bottom_right_grip, 0, Qt.AlignBottom | Qt.AlignRight
            )

            # Populate QListWidget
            self.populate_list_widget()

        except Exception as e:
            logger.error(f"Failed to set up UI: {e}")
            raise RuntimeError("Failed to initialize user interface")

    def center_window(self) -> None:
        """Center the window on the screen."""
        try:
            desktop = QApplication.desktop()
            if desktop is None:
                raise RuntimeError("Failed to get desktop")
                
            screen = desktop.screenGeometry()
            window_size = self.geometry()
            x = (screen.width() - window_size.width()) // 2
            y = (screen.height() - window_size.height()) // 2
            self.move(x, y)
        except Exception as e:
            logger.error(f"Failed to center window: {e}")

    def populate_list_widget(self) -> None:
        """Populate the list widget with error files."""
        try:
            if not self.error_files:
                logger.warning("No error files to populate list widget")
                return

            self.file_list_widget.clear()
            for info in self.error_files:
                try:
                    file_name = info.get("file_name")
                    if not file_name:
                        logger.warning("Found error info without file name")
                        continue
                    self.file_list_widget.addItem(str(file_name))
                except Exception as e:
                    logger.error(f"Failed to add item to list widget: {e}")
                    continue

            if self.file_list_widget.count() > 0:
                self.file_list_widget.setCurrentRow(0)
            else:
                logger.warning("No valid items added to list widget")

        except Exception as e:
            logger.error(f"Failed to populate list widget: {e}")
            self.custom_dialog_signal.emit("Failed to populate file list")

    def displayDetails(self, current_item: Any) -> None:
        """Display details for the selected item.

        Args:
            current_item: The currently selected item in the list widget.
        """
        try:
            if current_item is None:
                logger.debug("No item selected")
                return

            selected_file = current_item.text()
            if not selected_file:
                logger.warning("Selected item has no text")
                return

            selected_info = next(
                (info for info in self.error_files if info["file_name"] == selected_file), None
            )

            if not selected_info:
                logger.warning(f"No error info found for file: {selected_file}")
                return

            details_text = self._format_details_text(selected_info)
            self.details_display.setPlainText(details_text)

        except Exception as e:
            logger.error(f"Failed to display details: {e}")
            self.custom_dialog_signal.emit("Failed to display file details")

    def _format_details_text(self, info: Dict[str, Any]) -> str:
        """Format the details text for display.

        Args:
            info: Dictionary containing file error information.

        Returns:
            Formatted text string for display.
        """
        try:
            details = []
            details.append(f"File Name: {info['file_name']}")
            details.append(f"Error: {info['error']}")

            artist_found = info["artist_found"]
            album_found = info["album_found"]

            details.append(f"Artist Found: {artist_found[0] if artist_found else 'False'}")
            details.append(f"Album Found: {album_found[0] if album_found else 'False'}\n")

            details.append("Metadata:")
            metadata_dict = info["metadata_dict"]
            if metadata_dict:
                for key, value in metadata_dict.items():
                    details.append(f"{key}: {value}")
            else:
                details.append("No metadata available")

            return "\n".join(details)

        except Exception as e:
            logger.error(f"Failed to format details text: {e}")
            return "Error: Failed to format details"

    def copyDetails(self) -> None:
        """Copy the details to clipboard."""
        try:
            clipboard = QApplication.clipboard()
            if clipboard is None:
                raise RuntimeError("Failed to get clipboard")
                
            text = self.details_display.toPlainText()
            if not text:
                logger.warning("No text to copy to clipboard")
                return

            clipboard.setText(text)
            self.copy_button.setText("Success")
            self.copy_button.setStyleSheet(
                """
                background-color: rgba(255, 152, 152, 1);
                color: black;
            """
            )

            if hasattr(self, "reset_copy_timer"):
                self.reset_copy_timer.stop()

            self.reset_copy_timer = QTimer(self)
            self.reset_copy_timer.timeout.connect(self.resetCopyButton)
            self.reset_copy_timer.start(1000)

        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            self.custom_dialog_signal.emit("Failed to copy text to clipboard")

    def resetCopyButton(self) -> None:
        """Reset the copy button text and style."""
        self.copy_button.setText("Copy Bottom")
        self.copy_button.setStyleSheet("")

    def generateTXT(self) -> None:
        """Generate a text file with error details."""
        self._save_file_with_dialog(
            "Save TXT",
            "Text Files (*.txt)",
            self._generate_txt_content,
            "An error occurred while generating the TXT file.",
            self.txt_button,
        )

    def generateCSV(self) -> None:
        """Generate a CSV file with error details."""
        self._save_file_with_dialog(
            "Save CSV",
            "CSV Files (*.csv)",
            self._generate_csv_content,
            "An error occurred while generating the CSV file.",
            self.csv_button,
        )

    def generateJSON(self) -> None:
        """Generate a JSON file with error details."""
        self._save_file_with_dialog(
            "Save JSON",
            "JSON Files (*.json)",
            self._generate_json_content,
            "An error occurred while generating the JSON file.",
            self.json_button,
        )

    def _save_file_with_dialog(
        self,
        title: str,
        file_filter: str,
        save_function: Callable[[str], None],
        error_message: str,
        success_button: QPushButton,
    ) -> None:
        """Handle file saving with dialog manager."""
        try:
            file_path = DialogManager.get_save_file(
                self, 
                title, 
                file_filter, 
                Path(file_filter.split("*")[1].split(")")[0])
            )
            if file_path:
                self._save_file(str(file_path), save_function, error_message, success_button)
        except Exception as e:
            logger.error(f"Failed to handle file save dialog: {e}")
            self.custom_dialog_signal.emit(f"Failed to save file: {str(e)}")

    def _get_default_save_directory(self) -> Path:
        """Get platform-specific default save directory."""
        system = platform.system()
        try:
            if system == "Windows":
                return Path(os.path.expandvars("%USERPROFILE%/Documents"))
            elif system == "Darwin":
                return Path.home() / "Documents"
            else:  # Linux and others
                return Path.home() / "Documents"
        except Exception as e:
            logger.error(f"Failed to get default save directory: {e}")
            return Path.home()

    def _generate_txt_content(self, file_name: str) -> None:
        """Generate text file content.

        Args:
            file_name: Path to save the text file.
        """
        with open(file_name, "w", encoding="utf-8") as file:
            for info in self.error_files:
                file.write(self._format_details_text(info))
                file.write("\n\n")

    def _generate_csv_content(self, file_name: str) -> None:
        """Generate CSV file content.

        Args:
            file_name: Path to save the CSV file.
        """
        rows = []
        max_metadata_fields = max(len(info["metadata_dict"]) for info in self.error_files)

        # Generate rows
        for info in self.error_files:
            try:
                row = self._process_csv_row(info)
                rows.append(row)
            except Exception as e:
                logger.error(f"Failed to process CSV row: {e}")
                continue

        # Write to CSV file
        with open(file_name, mode="w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(self._generate_csv_header(max_metadata_fields))
            writer.writerows(rows)

    def _generate_json_content(self, file_name: str) -> None:
        """Generate JSON file content.

        Args:
            file_name: Path to save the JSON file.
        """
        data = []
        for info in self.error_files:
            try:
                row_data = self._process_json_data(info)
                data.append(row_data)
            except Exception as e:
                logger.error(f"Failed to process JSON data: {e}")
                continue

        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def _process_csv_row(self, info: Dict[str, Any]) -> List[str]:
        """Process a single row for CSV output.

        Args:
            info: Dictionary containing file information.

        Returns:
            List of values for the CSV row.
        """
        metadata_dict = self._format_metadata(info["metadata_dict"])

        artist_found = info["artist_found"][0] if info["artist_found"] else "None"
        album_found = info["album_found"][0] if info["album_found"] else "None"

        row = [info["file_name"], info["error"], artist_found, album_found]

        # Add metadata
        for key, value in metadata_dict.items():
            row.extend([key, value])

        return row

    def _process_json_data(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for JSON output.

        Args:
            info: Dictionary containing file information.

        Returns:
            Processed dictionary for JSON output.
        """
        metadata_dict = self._format_metadata(info["metadata_dict"])

        artist_found = info["artist_found"][0] if info["artist_found"] else "False"
        album_found = info["album_found"][0] if info["album_found"] else "False"

        return {
            "filename": info["file_name"],
            "error": info["error"],
            "artist_found": artist_found,
            "album_found": album_found,
            "metadata_dict": metadata_dict,
        }

    def _format_metadata(self, metadata_dict: Dict[str, Any]) -> Dict[str, str]:
        """Format metadata dictionary values to strings.

        Args:
            metadata_dict: Raw metadata dictionary

        Returns:
            Dictionary with string values
        """
        try:
            if not self._validate_metadata_dict(metadata_dict):
                logger.warning("Invalid metadata dictionary")
                return {}

            return {
                str(key): str(value) for key, value in metadata_dict.items() if value is not None
            }
        except Exception as e:
            logger.error(f"Failed to format metadata: {e}")
            return {}

    def _validate_metadata_dict(self, metadata_dict: Dict[str, Any]) -> bool:
        """Validate metadata dictionary structure.

        Args:
            metadata_dict: Dictionary containing metadata.

        Returns:
            True if valid, False otherwise.
        """
        try:
            if not isinstance(metadata_dict, dict):
                return False

            # Check all values can be converted to strings
            for value in metadata_dict.values():
                try:
                    str(value)
                except Exception:
                    return False

            return True

        except Exception as e:
            logger.error(f"Metadata validation error: {e}")
            return False

    def update_error_list(self, error_list: List[ErrorDict]) -> None:
        """Update the error list widget with new errors."""
        self.error_list = error_list
        self.current_error_index = 0
        self.update_current_error()

    def update_current_error(self):
        """Update the current error display."""
        if self.current_error_index < len(self.error_list):
            error = self.error_list[self.current_error_index]
            self.error_text.setText(error["error"])
            self.current_error_index += 1
        else:
            self.error_text.setText("No more errors.")

    def show_error_message(self, title, message):
        # Implement the logic to show an error message to the user
        print(f"{title}: {message}")

    def process_selected_action(self):
        try:
            # Implement the logic to process the selected action
            pass
        except Exception:
            self.show_error_message("Error", "Failed to process the selected action.")

    def clear_error_text(self) -> None:
        """Clear the error text display."""
        try:
            self.error_text.setText("")
            self.error_details.setText("")
        except Exception as e:
            logger.error(f"Failed to clear error text: {e}")

    def resetExcelButton(self) -> None:
        """Reset the Excel button text and style."""
        self.excel_button.setText("Generate Excel File")
        self.excel_button.setStyleSheet("")

    def generateExcel(self) -> None:
        """Generate Excel file with error details and proper error handling."""
        try:
            file_name = self._get_save_filename("Excel Files (*.xlsx)")
            if not file_name:
                return

            wb = openpyxl.Workbook()
            ws = wb.active

            headers = self._generate_excel_headers()
            ws.append(headers)

            for row_data in self._generate_excel_rows():
                ws.append(row_data)

            self._save_excel_file(wb, file_name)
            self._update_button_status(self.excel_button, "Excel File Generated!")

        except Exception as e:
            logger.error(f"Failed to generate Excel file: {e}")
            self.custom_dialog_signal.emit("Failed to generate Excel file")
            self._update_button_status(self.excel_button, "Excel Generation Failed!")

    def _generate_excel_headers(self) -> List[str]:
        """Generate Excel headers with metadata columns."""
        base_headers = ["Filename", "Error", "Artist Found", "Album Found"]
        metadata_headers = self._get_unique_metadata_keys()
        return base_headers + metadata_headers

    def _generate_excel_rows(self) -> List[List[str]]:
        """Generate Excel rows with proper formatting."""
        rows = []
        for info in self.error_files:
            try:
                row = self._format_excel_row(info)
                rows.append(row)
            except Exception as e:
                logger.error(f"Failed to format row for {info.get('file_name', 'unknown')}: {e}")
                continue
        return rows

    def _get_save_filename(self, file_filter: str) -> str:
        """Get a valid save filename from the user."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Excel", "", file_filter)
        return file_name

    def _save_excel_file(self, wb: openpyxl.Workbook, file_name: str) -> None:
        """Save the Excel workbook to a file."""
        try:
            wb.save(file_name)
        except Exception as e:
            logger.error(f"Failed to save Excel file: {e}")
            self.custom_dialog_signal.emit("Failed to save Excel file")

    def _update_button_status(self, button: QPushButton, status: str) -> None:
        """Update the button text and style to reflect the status."""
        button.setText(status)
        button.setStyleSheet(
            """
            background-color: rgba(255, 152, 152, 1);
            color: black;
        """
        )

    def _get_unique_metadata_keys(self) -> List[str]:
        """Get a list of unique metadata keys from all error files."""
        keys = set()
        for info in self.error_files:
            keys.update(info["metadata_dict"].keys())
        return sorted(list(keys))

    def _format_excel_row(self, info: Dict[str, Any]) -> List[str]:
        """Format a single row for Excel output."""
        row = [
            info["file_name"],
            info["error"],
            info["artist_found"][0] if info["artist_found"] else "None",
            info["album_found"][0] if info["album_found"] else "None",
        ]
        metadata_dict = self._format_metadata(info["metadata_dict"])
        for key, value in metadata_dict.items():
            row.append(str(value))
        return row

    def saveWindowState(self) -> None:
        """Save the current window state."""
        try:
            settings = QSettings()
            settings.setValue("MusicErrorWindow/geometry", self.saveGeometry())
            settings.setValue("MusicErrorWindow/windowState", self.saveState())
        except Exception as e:
            logger.error(f"Failed to save window state: {e}")

    def restoreWindowState(self) -> None:
        """Restore the previous window state and geometry."""
        try:
            settings = QSettings()
            geometry = settings.value("MusicErrorWindow/geometry")
            state = settings.value("MusicErrorWindow/windowState")

            if geometry:
                self.restoreGeometry(geometry)
            if state:
                self.restoreState(state)
        except Exception as e:
            logger.error(f"Failed to restore window state: {e}")
            self.center_window()  # Fallback to centered position

    def _validate_error_files(self, error_files: List[ErrorDict]) -> bool:
        """Validate the error files data structure.

        Args:
            error_files: List of dictionaries containing error information.

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            if not isinstance(error_files, list):
                logger.error("Error files must be a list")
                return False

            required_keys = {"file_name", "error", "artist_found", "album_found", "metadata_dict"}

            for error_file in error_files:
                if not isinstance(error_file, dict):
                    logger.error("Each error file must be a dictionary")
                    return False

                if not all(key in error_file for key in required_keys):
                    logger.error(
                        f"Missing required keys in error file: {required_keys - error_file.keys()}"
                    )
                    return False

                if not isinstance(error_file["metadata_dict"], dict):
                    logger.error("metadata_dict must be a dictionary")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating error files: {e}")
            return False

    def _configure_button(
        self,
        button: QPushButton,
        text: str,
        tooltip: str = "",
        size_policy: tuple = (QSizePolicy.Expanding, QSizePolicy.Fixed),
    ) -> None:
        """Configure a button with standard settings.

        Args:
            button: The button to configure
            text: Button text
            tooltip: Button tooltip text
            size_policy: Tuple of horizontal and vertical size policies
        """
        try:
            button.setText(text)
            if tooltip:
                button.setToolTip(tooltip)
            button.setSizePolicy(*size_policy)
            button.setObjectName(text.replace(" ", ""))

            # Set standard style
            button.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    border: 1px solid black;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 152, 152, 0.3);
                }
            """
            )
        except Exception as e:
            logger.error(f"Failed to configure button {text}: {e}")
            raise

    def _save_file(
        self,
        file_path: str,
        save_function: callable,
        error_message: str,
        success_button: QPushButton,
    ) -> None:
        """Save file with proper error handling and UI feedback."""
        try:
            save_function(file_path)
            success_button.setEnabled(False)
            success_button.setText("Generated")
            self.custom_dialog_signal.emit(f"File saved successfully: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            self.custom_dialog_signal.emit(f"{error_message}: {str(e)}")

    def _generate_csv_header(self, max_metadata_fields: int) -> List[str]:
        """Generate CSV file header based on the maximum number of metadata fields.

        Args:
            max_metadata_fields: Maximum number of metadata fields.

        Returns:
            List of column headers for the CSV file.
        """
        header = ["File Name", "Error", "Artist Found", "Album Found"]
        header.extend(
            [
                f"Key {i//2 + 1}" if i % 2 == 0 else f"Value {i//2 + 1}"
                for i in range(max_metadata_fields * 2)
            ]
        )
        return header

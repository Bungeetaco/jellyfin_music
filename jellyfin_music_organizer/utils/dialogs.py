from typing import Optional, List, Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox


def show_file_dialog(
    parent: Optional[QDialog] = None,
    title: str = "Select File",
    directory: Optional[Path] = None,
    file_types: Optional[List[str]] = None,
) -> Optional[Path]:
    """Show a file selection dialog."""
    file_types_str = ";;".join(file_types) if file_types else "All Files (*.*)"
    directory_str = str(directory) if directory else ""

    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        title,
        directory_str,
        file_types_str,
    )

    return Path(file_path) if file_path else None


def show_directory_dialog(
    parent: Optional[QDialog] = None,
    title: str = "Select Directory",
    directory: Optional[Path] = None,
) -> Optional[Path]:
    """Show a directory selection dialog."""
    directory_str = str(directory) if directory else ""

    dir_path = QFileDialog.getExistingDirectory(
        parent,
        title,
        directory_str,
        QFileDialog.Option.ShowDirsOnly,
    )

    return Path(dir_path) if dir_path else None


def show_message(
    title: str,
    message: str,
    message_type: QMessageBox.Icon = QMessageBox.Icon.Information,
    parent: Optional[QDialog] = None,
) -> None:
    """Show a message dialog."""
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(message_type)
    msg_box.exec()


def show_confirmation(
    title: str,
    message: str,
    parent: Optional[QDialog] = None,
) -> bool:
    """Show a confirmation dialog."""
    response = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return response == QMessageBox.StandardButton.Yes 
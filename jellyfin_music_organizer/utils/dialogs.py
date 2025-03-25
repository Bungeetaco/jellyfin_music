from typing import Optional, Tuple, List
from pathlib import Path
from PyQt5.QtWidgets import QFileDialog, QWidget
from .qt_types import QtConstants

class DialogManager:
    """Manage dialog operations with proper type safety."""

    @staticmethod
    def get_folder(
        parent: Optional[QWidget] = None,
        caption: str = "Select Folder",
        initial_dir: Optional[Path] = None
    ) -> Optional[Path]:
        """Show folder selection dialog."""
        try:
            folder = QFileDialog.getExistingDirectory(
                parent,
                caption,
                str(initial_dir) if initial_dir else "",
                QFileDialog.ShowDirsOnly
            )
            return Path(folder) if folder else None
        except Exception as e:
            logger.error(f"Failed to show folder dialog: {e}")
            return None

    @staticmethod
    def get_save_file(
        parent: Optional[QWidget] = None,
        caption: str = "Save File",
        initial_dir: Optional[Path] = None,
        filter_str: str = "All Files (*.*)"
    ) -> Optional[Path]:
        """Show save file dialog."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                parent,
                caption,
                str(initial_dir) if initial_dir else "",
                filter_str
            )
            return Path(file_path) if file_path else None
        except Exception as e:
            logger.error(f"Failed to show save file dialog: {e}")
            return None 
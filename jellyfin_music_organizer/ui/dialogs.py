"""Platform-specific dialog handling."""

from PyQt5.QtWidgets import QFileDialog, QWidget
from typing import Tuple, Optional
from pathlib import Path
import platform
import logging

logger = logging.getLogger(__name__)

class DialogManager:
    """Handle platform-specific dialog behavior."""

    @staticmethod
    def get_folder_dialog(
        parent: QWidget,
        title: str,
        start_dir: Optional[Path] = None
    ) -> Optional[Path]:
        """Show platform-appropriate folder selection dialog."""
        try:
            options = QFileDialog.Options()
            if platform.system() != "Darwin":
                options |= QFileDialog.DontUseNativeDialog

            if not start_dir:
                start_dir = Path.home()

            folder_path = QFileDialog.getExistingDirectory(
                parent,
                title,
                str(start_dir),
                options=options
            )

            return Path(folder_path) if folder_path else None

        except Exception as e:
            logger.error(f"Folder dialog failed: {e}")
            return None

    @staticmethod
    def get_save_file(
        parent: QWidget,
        title: str,
        filter_str: str,
        default_suffix: str
    ) -> Tuple[Optional[Path], str]:
        """Show platform-appropriate save file dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            filter_str: File type filter string
            default_suffix: Default file extension
            
        Returns:
            Tuple of (selected file path or None, selected filter)
        """
        try:
            options = QFileDialog.Options()
            
            if platform.system() != 'Darwin':  # Non-macOS
                options |= QFileDialog.DontUseNativeDialog
            
            file_name, selected_filter = QFileDialog.getSaveFileName(
                parent,
                title,
                str(Path.home()),
                filter_str,
                options=options
            )
            
            if file_name:
                path = Path(file_name)
                if not path.suffix:
                    path = path.with_suffix(default_suffix)
                return path, selected_filter
                
            return None, ""
            
        except Exception as e:
            logger.error(f"Save file dialog failed: {e}")
            return None, "" 
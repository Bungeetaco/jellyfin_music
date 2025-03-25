"""
File operations utility functions for the Jellyfin Music Organizer application.
"""

import os
import shutil
import stat
from logging import getLogger
from pathlib import Path
from typing import List, Optional

from .constants import SUPPORTED_AUDIO_EXTENSIONS
from .exceptions import FileOperationError

logger = getLogger(__name__)


def get_music_files(directory: str) -> List[Path]:
    """
    Get all music files in a directory and its subdirectories.

    Args:
        directory: Directory to search in

    Returns:
        List of paths to music files

    Raises:
        FileOperationError: If directory doesn't exist or is not accessible
    """
    try:
        pathlist: List[Path] = []
        for extension in SUPPORTED_AUDIO_EXTENSIONS:
            pathlist.extend(list(Path(directory).glob(f"**/*{extension}")))
        return pathlist
    except Exception as e:
        raise FileOperationError(f"Error scanning directory: {e}")


def create_directory(path: str, parents: bool = True) -> None:
    """
    Create a directory if it doesn't exist.

    Args:
        path: Directory path to create
        parents: Whether to create parent directories

    Raises:
        FileOperationError: If directory creation fails
    """
    try:
        Path(path).mkdir(parents=parents, exist_ok=True)
    except Exception as e:
        raise FileOperationError(f"Error creating directory: {e}")


def copy_file(source: str, destination: str, preserve_metadata: bool = True) -> None:
    """Copy a file with validation and error handling.

    Args:
        source: Source file path
        destination: Destination file path
        preserve_metadata: Whether to preserve file metadata

    Raises:
        FileOperationError: If file copy fails
    """
    try:
        source_path = Path(source)
        dest_path = Path(destination)

        # Validate paths
        if not source_path.exists():
            raise FileOperationError("Source file does not exist", str(source_path))
        if not os.access(source_path, os.R_OK):
            raise FileOperationError("Source file not readable", str(source_path))

        # Create destination directory if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        if preserve_metadata:
            shutil.copy2(source_path, dest_path)
        else:
            shutil.copy(source_path, dest_path)

        # Verify copy
        if not dest_path.exists():
            raise FileOperationError("Copy verification failed", str(dest_path))

    except Exception as e:
        logger.error(f"File copy failed: {e}")
        raise FileOperationError(f"Copy failed: {str(e)}", str(source_path))


def file_exists(path: str) -> bool:
    """
    Check if a file exists.

    Args:
        path: File path to check

    Returns:
        True if file exists, False otherwise
    """
    return Path(path).exists()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename

    Raises:
        FileOperationError: If filename is invalid or would be empty after sanitization
    """
    try:
        # Input validation
        if not isinstance(filename, str):
            raise FileOperationError(f"Expected string, got {type(filename)}")

        if not filename.strip():
            raise FileOperationError("Empty filename provided")

        # Remove invalid characters
        invalid_chars: str = ":*?<>|"
        translation_table = str.maketrans("", "", invalid_chars)
        sanitized = filename.translate(translation_table)

        # Additional sanitization
        sanitized = sanitized.replace("/", "").replace("\\", "")
        sanitized = sanitized.replace('"', "").replace("'", "")
        sanitized = sanitized.replace("...", "").strip()

        # Validate result
        if not sanitized:
            raise FileOperationError("Filename would be empty after sanitization")

        return sanitized

    except Exception as e:
        logger.error(f"Failed to sanitize filename '{filename}': {e}")
        raise FileOperationError(f"Failed to sanitize filename: {str(e)}")


def get_file_size(path: str) -> Optional[int]:
    """
    Get the size of a file in bytes.

    Args:
        path: File path

    Returns:
        File size in bytes or None if file doesn't exist
    """
    try:
        return os.path.getsize(path)
    except OSError:
        return None


def safe_remove(path: str) -> None:
    """Safely remove a file with validation.

    Args:
        path: Path to file to remove

    Raises:
        FileOperationError: If file removal fails
    """
    try:
        file_path = Path(path)
        if file_path.exists():
            if not os.access(file_path, os.W_OK):
                raise FileOperationError("File not writable", str(file_path))
            file_path.unlink()
    except Exception as e:
        logger.error(f"File removal failed: {e}")
        raise FileOperationError(f"Remove failed: {str(e)}", str(path))


class FileOperations:
    """Platform-independent file operations."""

    @staticmethod
    def ensure_writable(path: Path) -> None:
        """Ensure path is writable on all platforms.

        Args:
            path: Path to make writable

        Raises:
            FileOperationError: If path cannot be made writable
        """
        try:
            if os.name == "nt":  # Windows
                if path.exists() and not os.access(path, os.W_OK):
                    os.chmod(path, stat.S_IWRITE)
            else:  # Unix-like
                if path.exists():
                    path.chmod(path.stat().st_mode | stat.S_IWRITE)
        except Exception as e:
            logger.error(f"Failed to make path writable: {e}")
            raise FileOperationError(f"Cannot make path writable: {e}", str(path))

    @staticmethod
    def safe_copy(source: Path, destination: Path, overwrite: bool = False) -> None:
        """Copy file safely across platforms.

        Args:
            source: Source path
            destination: Destination path
            overwrite: Whether to overwrite existing files

        Raises:
            FileOperationError: If copy operation fails
        """
        try:
            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)

            if destination.exists():
                if not overwrite:
                    raise FileOperationError("Destination exists", str(destination))
                FileOperations.ensure_writable(destination)
                destination.unlink()

            # Copy with metadata preservation
            shutil.copy2(source, destination)

        except Exception as e:
            logger.error(f"File copy failed: {e}")
            raise FileOperationError(f"Copy failed: {e}", str(source))

    @staticmethod
    def safe_remove(path: Path) -> None:
        """Remove file safely across platforms.

        Args:
            path: Path to remove

        Raises:
            FileOperationError: If removal fails
        """
        try:
            if not path.exists():
                return

            FileOperations.ensure_writable(path)
            if path.is_file():
                path.unlink()
            else:
                shutil.rmtree(path)
        except Exception as e:
            logger.error(f"File removal failed: {e}")
            raise FileOperationError(f"Remove failed: {e}", str(path))

    @staticmethod
    def get_legal_filename(filename: str) -> str:
        """Get legal filename for current platform.

        Args:
            filename: Original filename

        Returns:
            Legal filename for current platform
        """
        if os.name == "nt":  # Windows
            illegal_chars = '<>:"/\\|?*'
            max_length = 255
        else:  # Unix-like
            illegal_chars = "/"
            max_length = 255

        # Replace illegal characters
        for char in illegal_chars:
            filename = filename.replace(char, "_")

        # Truncate if too long
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[: max_length - len(ext)] + ext

        return filename.strip()

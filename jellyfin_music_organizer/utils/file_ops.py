"""
File operations utility functions for the Jellyfin Music Organizer application.
"""

import os
import shutil
from functools import wraps
from logging import getLogger
from pathlib import Path
from typing import Any, Callable, List, Optional, TypeVar

from .constants import SUPPORTED_AUDIO_EXTENSIONS
from .error_handler import handle_errors
from .exceptions import FileOperationError

logger = getLogger(__name__)

T = TypeVar("T")  # For generic return type


def with_error_handling(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for handling file operation errors.

    Args:
        func: Function to wrap with error handling

    Returns:
        Wrapped function
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"File operation failed: {e}")
            raise FileOperationError(f"Operation failed: {str(e)}")

    return wrapper


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
    """Safe file operations with proper error handling."""

    @staticmethod
    @with_error_handling
    def ensure_writable(path: Path) -> bool:
        """Ensure a path is writable.

        Args:
            path: Path to check/make writable

        Returns:
            True if path is or was made writable, False otherwise
        """
        if path.exists():
            if os.access(path, os.W_OK):
                return True
            # Try to make it writable
            try:
                path.chmod(path.stat().st_mode | 0o200)
                return True
            except Exception:
                return False
        return True

    @staticmethod
    @with_error_handling
    def safe_copy(
        source: Path, destination: Path, overwrite: bool = False, preserve_metadata: bool = True
    ) -> bool:
        """Safely copy a file with metadata preservation.

        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing files
            preserve_metadata: Whether to preserve file metadata

        Returns:
            True if copy was successful

        Raises:
            FileOperationError: If copy operation fails
            FileNotFoundError: If source file doesn't exist
            FileExistsError: If destination exists and overwrite is False
            PermissionError: If paths aren't writable
        """
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        if destination.exists() and not overwrite:
            raise FileExistsError(f"Destination file exists: {destination}")

        # Ensure destination directory exists
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Ensure both paths are writable
        if not FileOperations.ensure_writable(source):
            raise PermissionError(f"Source file not writable: {source}")
        if not FileOperations.ensure_writable(destination):
            raise PermissionError(f"Destination path not writable: {destination}")

        # Copy with metadata preservation if requested
        if preserve_metadata:
            shutil.copy2(source, destination)
        else:
            shutil.copy(source, destination)
        return True

    @staticmethod
    def is_audio_file(path: Path) -> bool:
        """Check if a file is a supported audio file.

        Args:
            path: Path to check

        Returns:
            True if file is a supported audio file
        """
        return path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS

    @staticmethod
    def get_legal_filename(filename: str, max_length: int = 255) -> str:
        """Generate a legal filename.

        Args:
            filename: Original filename
            max_length: Maximum length for filename

        Returns:
            Legal filename
        """
        # Replace illegal characters
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, "_")

        # Handle special cases
        filename = filename.strip(". ")  # Remove leading/trailing dots and spaces

        # Truncate if necessary
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            max_name_length = max_length - len(ext)
            filename = name[:max_name_length] + ext

        return filename or "_"  # Return '_' if filename would be empty

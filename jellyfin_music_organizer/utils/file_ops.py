"""
File operations utility functions for the Jellyfin Music Organizer application.
"""

import os
import shutil
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


def copy_file(source: str, destination: str) -> None:
    """
    Copy a file to a new location.

    Args:
        source: Source file path
        destination: Destination file path

    Raises:
        FileOperationError: If file copy fails
    """
    try:
        shutil.copy(source, destination)
    except Exception as e:
        raise FileOperationError(f"Error copying file: {e}")


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

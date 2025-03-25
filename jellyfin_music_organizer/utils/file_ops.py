"""
File operations utility functions for the Jellyfin Music Organizer application.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional

from .constants import SUPPORTED_AUDIO_EXTENSIONS
from .exceptions import FileOperationError


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
    """
    # Remove invalid characters
    invalid_chars = ":*?<>|"
    sanitized = filename.translate(str.maketrans("", "", invalid_chars))

    # Replace problematic characters
    sanitized = sanitized.replace("/", "").replace("\\", "")
    sanitized = sanitized.replace('"', "").replace("'", "")
    sanitized = sanitized.replace("...", "")

    # Strip whitespace
    return sanitized.strip()


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

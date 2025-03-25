"""
Custom exceptions for the Jellyfin Music Organizer application.
"""

from typing import Optional


class JellyfinMusicOrganizerError(Exception):
    """Base exception for Jellyfin Music Organizer."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.message: str = message


class ConfigurationError(JellyfinMusicOrganizerError):
    """Raised when there's an error with configuration."""


class MetadataError(JellyfinMusicOrganizerError):
    """Raised when there's an error with music file metadata."""


class FileOperationError(JellyfinMusicOrganizerError):
    """Raised when there's an error with file operations."""

    def __init__(self, message: str, file_path: Optional[str] = None) -> None:
        """Initialize the file operation error."""
        super().__init__(message)
        self.file_path: Optional[str] = file_path


class AudioPlaybackError(JellyfinMusicOrganizerError):
    """Raised when there's an error playing audio."""

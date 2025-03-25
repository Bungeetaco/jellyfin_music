"""
Custom exceptions for the Jellyfin Music Organizer application.
"""

from typing import Optional


class JellyfinMusicOrganizerError(Exception):
    """Base exception for all application errors."""


class ConfigurationError(JellyfinMusicOrganizerError):
    """Raised when there's an error with configuration."""

    def __init__(self, message: str, config_key: Optional[str] = None) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            config_key: Optional configuration key that caused the error
        """
        super().__init__(message)
        self.config_key = config_key
        self.message = message

    def __str__(self) -> str:
        """Return formatted error message."""
        if self.config_key:
            return f"{self.message} (Key: {self.config_key})"
        return self.message


class MetadataError(JellyfinMusicOrganizerError):
    """Raised when there's an error with music file metadata."""


class FileOperationError(JellyfinMusicOrganizerError):
    """Raised when there's an error with file operations."""

    def __init__(self, message: str, file_path: Optional[str] = None) -> None:
        """Initialize file operation error.

        Args:
            message: Error message
            file_path: Optional path to file that caused the error
        """
        super().__init__(message)
        self.file_path = file_path
        self.message = message

    def __str__(self) -> str:
        """Return formatted error message."""
        if self.file_path:
            return f"{self.message} (File: {self.file_path})"
        return self.message


class AudioPlaybackError(JellyfinMusicOrganizerError):
    """Raised when there's an error playing audio."""


class ResourceError(JellyfinMusicOrganizerError):
    """Exception raised for resource loading or management errors."""

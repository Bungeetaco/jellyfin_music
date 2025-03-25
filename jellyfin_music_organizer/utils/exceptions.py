"""
Custom exceptions for the Jellyfin Music Organizer application.
"""


class JellyfinMusicOrganizerError(Exception):
    """Base exception class for the application."""


class ConfigurationError(JellyfinMusicOrganizerError):
    """Raised when there's an error with configuration."""


class MetadataError(JellyfinMusicOrganizerError):
    """Raised when there's an error with music file metadata."""


class FileOperationError(JellyfinMusicOrganizerError):
    """Raised when there's an error with file operations."""


class AudioPlaybackError(JellyfinMusicOrganizerError):
    """Raised when there's an error playing audio."""

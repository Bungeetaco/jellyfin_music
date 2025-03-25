"""
Custom exceptions for the Jellyfin Music Organizer application.
"""


class JellyfinMusicOrganizerError(Exception):
    """Base exception class for the application."""

    pass


class ConfigurationError(JellyfinMusicOrganizerError):
    """Raised when there's an error with configuration."""

    pass


class MetadataError(JellyfinMusicOrganizerError):
    """Raised when there's an error with music file metadata."""

    pass


class FileOperationError(JellyfinMusicOrganizerError):
    """Raised when there's an error with file operations."""

    pass


class AudioPlaybackError(JellyfinMusicOrganizerError):
    """Raised when there's an error playing audio."""

    pass

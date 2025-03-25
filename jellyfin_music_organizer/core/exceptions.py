from typing import Optional


class JellyfinMusicOrganizerError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.cause = cause


class FileOperationError(JellyfinMusicOrganizerError):
    """Raised when file operations fail."""



class MetadataError(JellyfinMusicOrganizerError):
    """Raised when metadata operations fail."""



class ConfigurationError(JellyfinMusicOrganizerError):
    """Raised when configuration operations fail."""



class ResourceError(JellyfinMusicOrganizerError):
    """Raised when resource operations fail."""



class UIError(JellyfinMusicOrganizerError):
    """Base class for UI-related errors."""



class WindowError(UIError):
    """Raised when window operations fail."""



class DialogError(UIError):
    """Raised when dialog operations fail."""


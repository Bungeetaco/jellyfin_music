from typing import Optional

class JellyfinMusicOrganizerError(Exception):
    """Base exception for Jellyfin Music Organizer."""
    
    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.cause = cause

class FileOperationError(JellyfinMusicOrganizerError):
    """Raised when a file operation fails."""
    pass

class MetadataError(JellyfinMusicOrganizerError):
    """Raised when metadata operations fail."""
    pass

class ConfigurationError(JellyfinMusicOrganizerError):
    """Raised when configuration is invalid or missing."""
    pass

class ResourceError(JellyfinMusicOrganizerError):
    """Raised when a resource cannot be loaded."""
    pass

class UIError(JellyfinMusicOrganizerError):
    """Raised when a UI operation fails."""
    pass

class WindowError(UIError):
    """Raised when window operations fail."""
    pass

class DialogError(UIError):
    """Raised when dialog operations fail."""
    pass 
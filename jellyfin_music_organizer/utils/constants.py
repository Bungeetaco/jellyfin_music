"""
Constants used throughout the Jellyfin Music Organizer application.
"""

from pathlib import Path
from typing import Dict, List, Set
import os

# Application metadata
class AppInfo:
    """Application information constants."""
    NAME: str = "Jellyfin Music Organizer"
    VERSION: str = "3.06"
    AUTHOR: str = "Gabriel"

# File extensions
class AudioFormats:
    """Supported audio format constants."""
    EXTENSIONS: Set[str] = {
        ".aif", ".aiff", ".ape", ".flac", ".m4a", ".m4b",
        ".m4r", ".mp2", ".mp3", ".mp4", ".mpc", ".ogg",
        ".opus", ".wav", ".wma"
    }

    @classmethod
    def is_supported(cls, extension: str) -> bool:
        """Check if file extension is supported.
        
        Args:
            extension: File extension to check
            
        Returns:
            bool: True if supported, False otherwise
        """
        return extension.lower() in cls.EXTENSIONS

# Metadata configuration
class MetadataTags:
    """Metadata tag constants."""
    TAGS: Dict[str, List[str]] = {
        "artist": ["©art", "artist", "author", "tpe1"],
        "album": ["©alb", "album", "talb", "wm/albumtitle"],
    }

    @classmethod
    def get_tags(cls, tag_type: str) -> List[str]:
        """Get metadata tags for a specific type.
        
        Args:
            tag_type: Type of metadata tags to get
            
        Returns:
            List of tag names
        """
        return cls.TAGS.get(tag_type, [])

# UI Configuration
class UIConfig:
    """UI configuration constants."""
    WINDOW_DIMENSIONS = {"width": 400, "height": 260, "x": 100, "y": 100}
    TITLE_BAR_HEIGHT = 32
    ICON_SIZE = 24
    
    # UI Styles
    STYLES: Dict[str, str] = {
        "title_bar_button": (
            "QPushButton {"
            "   color: white;"
            "   background-color: transparent;"
            "} "
            "QPushButton:hover {"
            "   background-color: {color};"
            "}"
        ),
        "progress_bar": (
            "QProgressBar {"
            "   border: 1px solid black;"
            "   text-align: center;"
            "   color: black;"
            "   background-color: rgba(255, 152, 152, 1);"
            "} "
            "QProgressBar::chunk {"
            "   background-color: rgba(255, 152, 152, 1);"
            "}"
        ),
    }

# File paths
class Paths:
    """File path constants."""
    CONFIG_FILE = Path("settings_jmo.json")
    LOG_DIR = Path("logs")
    LOG_FILE = LOG_DIR / "app.log"
    
    @classmethod
    def ensure_paths(cls) -> None:
        """Ensure all required paths exist."""
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

# Error messages
class ErrorMessages:
    """Error message constants."""
    MESSAGES: Dict[str, str] = {
        "NO_METADATA": "No metadata found in file",
        "INVALID_FORMAT": "Invalid file format",
        "MISSING_REQUIRED": "Missing required metadata fields",
        "NETWORK_ERROR": "Network connection error",
        "PERMISSION_ERROR": "Permission denied",
        "UNKNOWN_ERROR": "An unknown error occurred",
    }

    @classmethod
    def get(cls, key: str, default: str = "") -> str:
        """Get error message by key.
        
        Args:
            key: Message key
            default: Default message if key not found
            
        Returns:
            Error message
        """
        return cls.MESSAGES.get(key, default)

# Notification sounds
NOTIFICATION_SOUNDS: Dict[str, str] = {"ding": "audio_ding", "complete": "audio_complete"}

# Notification configuration
class NotificationConfig:
    """Notification configuration constants."""
    
    SOUNDS = {
        "default": {
            "windows": "SystemDefault",
            "darwin": "Tink",
            "linux": "bell",
            "fallback": "audio_ding.wav"
        },
        "complete": {
            "windows": "SystemAsterisk",
            "darwin": "Glass",
            "linux": "complete",
            "fallback": "audio_complete.wav"
        },
        "error": {
            "windows": "SystemHand",
            "darwin": "Basso",
            "linux": "dialog-error",
            "fallback": "audio_error.wav"
        }
    }

    @classmethod
    def get_sound(cls, sound_type: str, platform: str) -> str:
        """Get appropriate sound for platform.
        
        Args:
            sound_type: Type of sound requested
            platform: Platform identifier
            
        Returns:
            Sound identifier for platform
        """
        return cls.SOUNDS.get(sound_type, {}).get(platform, 
               cls.SOUNDS.get(sound_type, {}).get("fallback"))

# Initialize paths
Paths.ensure_paths()

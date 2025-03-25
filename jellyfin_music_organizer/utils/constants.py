"""
Constants used throughout the Jellyfin Music Organizer application.
"""

from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Set


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
        ".aif",
        ".aiff",
        ".ape",
        ".flac",
        ".m4a",
        ".m4b",
        ".m4r",
        ".mp2",
        ".mp3",
        ".mp4",
        ".mpc",
        ".ogg",
        ".opus",
        ".wav",
        ".wma",
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
class UIConstants:
    """UI-related constants."""

    WINDOW_DIMENSIONS: Final[Dict[str, int]] = {"width": 400, "height": 260, "x": 100, "y": 100}

    TITLE_BAR_HEIGHT: Final[int] = 32
    ICON_SIZE: Final[int] = 24
    BUTTON_SIZE: Final[int] = 24

    STYLE_TEMPLATES: Final[Dict[str, str]] = {
        "title_bar": """
            QWidget#TitleBar {
                background-color: %(bg_color)s;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
        """,
        "button": """
            QPushButton {
                background-color: transparent;
                color: %(text_color)s;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: %(hover_color)s;
            }
        """,
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
            "fallback": "audio_ding.wav",
        },
        "complete": {
            "windows": "SystemAsterisk",
            "darwin": "Glass",
            "linux": "complete",
            "fallback": "audio_complete.wav",
        },
        "error": {
            "windows": "SystemHand",
            "darwin": "Basso",
            "linux": "dialog-error",
            "fallback": "audio_error.wav",
        },
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
        sound_dict = cls.SOUNDS.get(sound_type, {})
        platform_sound = sound_dict.get(platform)
        return platform_sound if platform_sound is not None else sound_dict.get("fallback", "")


# Initialize paths
Paths.ensure_paths()


def get_metadata_value(metadata: Dict[str, Any], key: str, default: Optional[str] = None) -> str:
    """Safely get metadata value with proper type handling."""
    value = metadata.get(key, default)
    if isinstance(value, list):
        return value[0] if value else default or ""
    return str(value) if value is not None else default or ""


# Audio file extensions
SUPPORTED_AUDIO_EXTENSIONS: Set[str] = {".mp3", ".m4a", ".flac", ".ogg", ".wav", ".wma", ".aac"}

# Metadata tags
METADATA_TAGS: Set[str] = {
    "title",
    "artist",
    "album",
    "albumartist",
    "date",
    "genre",
    "tracknumber",
}


class FileType(Enum):
    """Enumeration of supported file types."""

    MP3 = auto()
    FLAC = auto()
    M4A = auto()
    OGG = auto()
    WAV = auto()
    WMA = auto()
    AAC = auto()


class MetadataFields(Enum):
    """Enumeration of metadata fields."""

    TITLE = "title"
    ARTIST = "artist"
    ALBUM = "album"
    ALBUM_ARTIST = "albumartist"
    TRACK_NUMBER = "tracknumber"
    DISC_NUMBER = "discnumber"
    YEAR = "date"
    GENRE = "genre"


class FileConstants:
    """File-related constants."""

    SUPPORTED_EXTENSIONS: Final[Set[str]] = {
        ".mp3",
        ".flac",
        ".m4a",
        ".ogg",
        ".wav",
        ".wma",
        ".aac",
    }

    MAX_FILENAME_LENGTH: Final[int] = 255
    BUFFER_SIZE: Final[int] = 8192  # 8KB buffer for file operations

    METADATA_ENCODING: Final[str] = "utf-8"

    @staticmethod
    def is_supported_extension(ext: str) -> bool:
        """Check if file extension is supported."""
        return ext.lower() in FileConstants.SUPPORTED_EXTENSIONS


class ConfigConstants:
    """Configuration-related constants."""

    DEFAULT_CONFIG: Final[Dict[str, Any]] = {
        "music_folder_path": "",
        "destination_folder_path": "",
        "mute_sound": False,
        "version": "3.06",
        "window_state": {},
        "platform_specific": {},
    }

    CONFIG_VERSION: Final[str] = "3.06"
    CONFIG_FILENAME: Final[str] = "config.json"

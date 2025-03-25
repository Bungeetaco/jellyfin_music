"""
Constants used throughout the Jellyfin Music Organizer application.
"""

from typing import List, Dict, Any

# Application metadata
APP_NAME: str = "Jellyfin Music Organizer"
APP_VERSION: str = "3.06"
APP_AUTHOR: str = "Gabriel"

# Supported audio file extensions
SUPPORTED_AUDIO_EXTENSIONS: List[str] = [
    ".aif", ".aiff", ".ape", ".flac", ".m4a", ".m4b", ".m4r",
    ".mp2", ".mp3", ".mp4", ".mpc", ".ogg", ".opus", ".wav", ".wma"
]

# Metadata tags to search for
METADATA_TAGS: Dict[str, List[str]] = {
    "artist": ['©art', 'artist', 'author', 'tpe1'],
    "album": ['©alb', 'album', 'talb', 'wm/albumtitle']
}

# Window dimensions
WINDOW_DIMENSIONS: Dict[str, int] = {
    "width": 400,
    "height": 260,
    "x": 100,
    "y": 100
}

# Title bar dimensions
TITLE_BAR_HEIGHT: int = 32
ICON_SIZE: int = 24

# Notification sounds
NOTIFICATION_SOUNDS: Dict[str, str] = {
    "ding": "audio_ding",
    "complete": "audio_complete"
}

# File paths
CONFIG_FILE: str = "settings_jmo.json"
LOG_FILE: str = "logs/app.log"

# UI styles
STYLES: Dict[str, str] = {
    "title_bar_button": """
        QPushButton { 
            color: white; 
            background-color: transparent; 
        }
        QPushButton:hover { 
            background-color: {color}; 
        }
    """,
    "progress_bar_complete": """
        QProgressBar {
            border: 1px solid black;
            text-align: center;
            color: black;
            background-color: rgba(255, 152, 152, 1);
        }
        QProgressBar::chunk {
            background-color: rgba(255, 152, 152, 1);
        }
    """
} 
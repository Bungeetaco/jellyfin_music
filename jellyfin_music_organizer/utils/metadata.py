"""
Metadata operations utility functions for the Jellyfin Music Organizer application.
"""

from logging import getLogger
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import mutagen
from mutagen.asf import ASFUnicodeAttribute

from .constants import MetadataTags
from .exceptions import MetadataError
from .file_ops import sanitize_filename
from .typing_compat import MetadataValue

logger = getLogger(__name__)


def extract_metadata(file_path: str) -> Dict[str, MetadataValue]:
    """
    Extract metadata from a music file.

    Args:
        file_path: Path to the music file

    Returns:
        Dictionary containing metadata

    Raises:
        MetadataError: If metadata extraction fails
    """
    try:
        metadata = mutagen.File(file_path)
        if metadata is None:
            raise MetadataError("Could not read file metadata")

        return {tag: metadata.get(tag, "") for tag in MetadataTags.get_tags("all")}
    except Exception as e:
        raise MetadataError(f"Failed to extract metadata: {e}")


def _convert_to_string(value: Union[str, List[str], ASFUnicodeAttribute]) -> str:
    """Convert metadata value to string safely.
    
    Args:
        value: Metadata value to convert
        
    Returns:
        String representation of the value
    """
    if isinstance(value, str):
        return value
    if isinstance(value, ASFUnicodeAttribute):
        return str(value)
    if isinstance(value, list) and value:
        first_value = value[0]
        if isinstance(first_value, ASFUnicodeAttribute):
            return str(first_value)
        return str(first_value)
    return ""


def get_artist_album(metadata: Dict[str, Any]) -> Tuple[str, str]:
    """
    Extract artist and album information from metadata.

    Args:
        metadata: Dictionary containing metadata

    Returns:
        Tuple of (artist, album) strings

    Raises:
        MetadataError: If metadata is invalid or missing required fields
    """
    if not isinstance(metadata, dict):
        raise MetadataError("Invalid metadata format")

    try:
        artist_data: Optional[Union[str, List[str], ASFUnicodeAttribute]] = None
        album_data: Optional[Union[str, List[str], ASFUnicodeAttribute]] = None

        # Search for artist and album tags
        for key, value in metadata.items():
            if not isinstance(key, str):
                continue

            lowercase_key = key.lower()
            if lowercase_key in MetadataTags.get_tags("artist"):
                artist_data = value
            elif lowercase_key in MetadataTags.get_tags("album"):
                album_data = value

        if not artist_data or not album_data:
            raise MetadataError("Missing artist or album information")

        # Convert to strings and handle special cases
        artist = _convert_to_string(artist_data)
        album = _convert_to_string(album_data)

        if not artist or not album:
            raise MetadataError("Empty artist or album value")

        return sanitize_filename(artist), sanitize_filename(album)

    except Exception as e:
        logger.error(f"Failed to extract metadata: {e}")
        raise MetadataError(f"Failed to extract metadata: {str(e)}")


def validate_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Validate that required metadata is present.

    Args:
        metadata: Dictionary containing metadata

    Returns:
        True if metadata is valid, False otherwise
    """
    try:
        artist, album = get_artist_album(metadata)
        return bool(artist and album)
    except MetadataError:
        return False


def get_metadata_value(metadata: Dict[str, MetadataValue], key: str, default: str = "") -> str:
    """Safely extract metadata value."""
    value = metadata.get(key)
    if value is None:
        return default

    if isinstance(value, (list, ASFUnicodeAttribute)):
        try:
            if isinstance(value, list):
                return str(value[0]) if value else default
            return str(value)
        except (IndexError, TypeError):
            return default
    return str(value)

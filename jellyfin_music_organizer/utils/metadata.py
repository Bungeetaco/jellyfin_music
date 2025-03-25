"""
Metadata operations utility functions for the Jellyfin Music Organizer application.
"""

from typing import Dict, Any, Optional, Tuple
import mutagen
from mutagen.asf import ASFUnicodeAttribute
from .exceptions import MetadataError
from .constants import METADATA_TAGS
from .file_ops import sanitize_filename

def extract_metadata(file_path: str) -> Dict[str, Any]:
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
            
        metadata_dict: Dict[str, Any] = {}
        for key, value in metadata.items():
            metadata_dict[key] = value
            
        return metadata_dict
    except Exception as e:
        raise MetadataError(f"Error extracting metadata: {e}")

def get_artist_album(metadata: Dict[str, Any]) -> Tuple[str, str]:
    """
    Extract artist and album information from metadata.
    
    Args:
        metadata: Dictionary containing metadata
        
    Returns:
        Tuple of (artist, album) strings
        
    Raises:
        MetadataError: If artist or album information is missing
    """
    artist_data: Optional[Any] = None
    album_data: Optional[Any] = None
    
    # Search for artist and album tags
    for key, value in metadata.items():
        lowercase_key = key.lower()
        if lowercase_key in METADATA_TAGS["artist"]:
            artist_data = value
        elif lowercase_key in METADATA_TAGS["album"]:
            album_data = value
            
    if not artist_data or not album_data:
        raise MetadataError("Missing artist or album information")
        
    # Convert to strings and handle special cases
    artist = str(artist_data[0]) if isinstance(artist_data[0], ASFUnicodeAttribute) else artist_data[0]
    album = str(album_data[0]) if isinstance(album_data[0], ASFUnicodeAttribute) else album_data[0]
    
    # Sanitize the values
    artist = sanitize_filename(artist)
    album = sanitize_filename(album)
    
    return artist, album

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
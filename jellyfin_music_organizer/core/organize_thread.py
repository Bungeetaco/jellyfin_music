"""
Thread for organizing music files based on their metadata.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

from mutagen.asf import ASFUnicodeAttribute
from PyQt5.QtCore import QThread, pyqtSignal

from ..utils.exceptions import MetadataError
from ..utils.file_ops import FileOperations
from .exceptions import FileOperationError

logger = logging.getLogger(__name__)


class OrganizeThread(QThread):
    """
    A QThread subclass that handles the music file organization process.

    This thread:
    1. Scans for music files in the selected directory
    2. Extracts metadata from each file
    3. Creates organized directory structure
    4. Handles file copying and error cases

    Signals:
        number_songs_signal (int): Emitted with total number of songs found
        music_progress_signal (int): Emitted with current progress percentage
        kill_thread_signal (str): Emitted to signal thread termination
        custom_dialog_signal (str): Emitted with custom dialog message
        organize_finish_signal (dict): Emitted with organization results
    """

    number_songs_signal: pyqtSignal = pyqtSignal(int)
    music_progress_signal: pyqtSignal = pyqtSignal(int)
    kill_thread_signal: pyqtSignal = pyqtSignal(str)
    custom_dialog_signal: pyqtSignal = pyqtSignal(str)
    organize_finish_signal: pyqtSignal = pyqtSignal(dict)

    def __init__(self, info: Dict[str, str]) -> None:
        """
        Initialize the OrganizeThread.

        Args:
            info: Dictionary containing source and destination folder paths
        """
        super().__init__()
        self.info = info
        self.remove_illegal_chars = True  # Default to True
        self.load_settings()

    def __del__(self) -> None:
        """Clean up by waiting for the thread to finish."""
        self.wait()

    def load_settings(self) -> None:
        """Load settings from the settings file."""
        try:
            with open("settings_jmo.json", "r") as f:
                settings = json.load(f)
                self.remove_illegal_chars = settings.get("remove_illegal_chars", True)
        except FileNotFoundError:
            pass  # Use default value

    def clean_filename(self, text: str) -> str:
        """
        Clean filename by removing or replacing illegal characters.

        Args:
            text: The text to clean

        Returns:
            str: The cleaned text
        """
        if self.remove_illegal_chars:
            # Remove characters that are not allowed in filenames
            text = (
                text.translate(str.maketrans("", "", ":*?<>|"))
                .replace("/", "")
                .replace("\\", "")
                .replace('"', "")
                .replace("'", "")
                .replace("...", "")
            )
        return text.strip()

    def run(self) -> None:
        """
        Main thread execution method.

        This method:
        1. Scans for music files
        2. Processes each file's metadata
        3. Creates organized directory structure
        4. Handles file copying and errors
        """
        try:
            # Supported audio file extensions
            extensions: List[str] = [
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
            ]

            # Generate list of paths to music files
            pathlist: List[Path] = []
            for extension in extensions:
                pathlist.extend(
                    list(Path(self.info["selected_music_folder_path"]).glob(f"**/*{extension}"))
                )

            # Update number of songs label
            total_number_of_songs: int = len(pathlist)
            self.number_songs_signal.emit(total_number_of_songs)

            # Define the artist and album values to search for
            artist_values: List[str] = ["©art", "artist", "author", "tpe1"]
            album_values: List[str] = ["©alb", "album", "talb"]

            # Check if folder has any songs
            if total_number_of_songs:
                # Initialize a dictionary to store file info for songs with errors
                recall_files: Dict[str, List[Dict[str, Any]]] = {
                    "error_files": [],
                    "replace_skip_files": [],
                }

                # Don't include replace_skip_files in progress bar
                i: int = 0

                # Loop through each song and organize it
                for path in pathlist:
                    # Replace backslashes with forward slashes
                    path_in_str: str = str(path).replace("\\", "/")
                    # Get file name from path
                    file_name: str = path_in_str.split("/")[-1]

                    # Reset variables
                    artist_data: Any = ""
                    album_data: Any = ""
                    file_info: Dict[str, Any] = {}

                    try:
                        # Load and extract metadata from the music file
                        metadata: Dict[str, str] = self.process_metadata(path)
                        if metadata is None:
                            raise ValueError(f"Could not load metadata from {path_in_str}")

                        # Loop through the metadata to find matching artist and album values
                        for key, value in metadata.items():
                            lowercase_key: str = key.lower()
                            if lowercase_key in artist_values:
                                artist_data = value
                            elif lowercase_key in album_values:
                                album_data = value

                        # Check if artist_data and album_data were found
                        if artist_data == "" or album_data == "":
                            raise Exception("Artist or album data not found")

                        # Convert the metadata values to strings
                        artist: str = (
                            str(artist_data[0])
                            if isinstance(artist_data[0], ASFUnicodeAttribute)
                            else artist_data[0]
                        )
                        album: str = (
                            str(album_data[0])
                            if isinstance(album_data[0], ASFUnicodeAttribute)
                            else album_data[0]
                        )

                        # Clean the artist and album names
                        artist = self.clean_filename(artist)
                        album = self.clean_filename(album)

                        # Construct new location
                        new_location: str = (
                            f"{self.info['selected_destination_folder_path']}/{artist}/{album}"
                        )

                        # Check if the file already exists in the new location
                        if Path(f"{new_location}/{file_name}").exists():
                            file_info = self._handle_existing_file(
                                file_name, new_location, path_in_str
                            )

                            recall_files["replace_skip_files"].append(file_info)
                        else:
                            # Create directory and copy file to new location
                            self.organize_file(path, metadata)

                    except Exception as e:
                        file_info = self._create_error_info(
                            file_name, artist_data, album_data, metadata, str(e)
                        )

                        recall_files["error_files"].append(file_info)

                    finally:
                        # Update progress bar if no error or 'File already exists'
                        if (
                            not file_info.get("error")
                            or file_info.get("error")
                            != "File already exists in the destination folder"
                        ):
                            i += 1
                            self.music_progress_signal.emit(int(i / len(pathlist) * 100))

                # Send recall_files
                self.organize_finish_signal.emit(recall_files)

            else:
                # No songs were found
                self.custom_dialog_signal.emit("No songs were found in the selected folder.")
                self.kill_thread_signal.emit("organize")
        except Exception as e:
            logger.error(f"Organization thread error: {e}")
            self.custom_dialog_signal.emit(f"Organization failed: {str(e)}")
            self.kill_thread_signal.emit("organize")

    def _handle_existing_file(
        self, file_name: str, new_location: str, path_in_str: str
    ) -> Dict[str, str]:
        """Handle case when file already exists in destination.

        Args:
            file_name: Name of the file
            new_location: Destination path
            path_in_str: Source path

        Returns:
            Dictionary with file information
        """
        return {
            "file_name": file_name,
            "new_location": new_location,
            "path_in_str": path_in_str,
            "error": "File already exists in the destination folder",
        }

    def organize_file(self, source: Path, metadata: Dict[str, str]) -> None:
        """Organize a single file based on its metadata."""
        try:
            # Create destination path from metadata
            dest = self._create_destination_path(metadata)

            # Ensure destination directory exists
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Copy file with metadata preservation
            FileOperations.safe_copy(source, dest, preserve_metadata=True)
        except Exception as e:
            raise FileOperationError(f"Failed to organize file: {e}")

    def _validate_path(self, path: str) -> bool:
        """Validate path exists and is accessible.

        Args:
            path: Path to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            path_obj = Path(path)
            return path_obj.exists() and os.access(path_obj, os.R_OK)
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return False

    def _create_error_info(
        self,
        file_name: str,
        artist_data: List[str],
        album_data: List[str],
        metadata_dict: Dict[str, Any],
        error: str,
    ) -> Dict[str, Any]:
        """Create error information dictionary.

        Args:
            file_name: Name of the file
            artist_data: Artist information
            album_data: Album information
            metadata_dict: File metadata
            error: Error message

        Returns:
            Dictionary containing error information
        """
        return {
            "file_name": file_name,
            "artist_found": artist_data,
            "album_found": album_data,
            "metadata_dict": metadata_dict,
            "error": str(error),
        }

    def process_metadata(self, file_path: Path) -> Dict[str, str]:
        """Process metadata from file."""
        try:
            # Direct return without intermediate variable
            return self.metadata_handler.extract_metadata(file_path)
        except Exception as e:
            raise MetadataError(f"Failed to process metadata: {e}")

    def process_file(self, file_path: Path) -> Dict[str, str]:
        """Process a single file."""
        return self.process_metadata(file_path)  # Reuse existing method

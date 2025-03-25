"""
Logging configuration for the Jellyfin Music Organizer application.
"""

import logging
from typing import Optional


def setup_logger(log_file: Optional[str] = None) -> logging.Logger:
    """Set up and configure the application logger."""
    logger = logging.getLogger("jellyfin_music_organizer")
    logger.setLevel(logging.INFO)

    # Add file handler if log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

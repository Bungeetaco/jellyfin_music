"""
Logging configuration for the Jellyfin Music Organizer application.
"""

import logging
import os
from pathlib import Path
from typing import Optional


def setup_logger(log_level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up the application logger.

    Args:
        log_level: The logging level to use
        log_file: Optional path to the log file

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger("jellyfin_music_organizer")
    logger.setLevel(log_level)

    # Create formatters
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")

    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

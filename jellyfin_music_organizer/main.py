"""
Main entry point for the Jellyfin Music Organizer application.
"""

import logging
import sys
from typing import Optional

from PyQt5.QtWidgets import QApplication

from .ui.music_organizer import MusicOrganizer
from .utils.config import ConfigManager
from .utils.constants import CONFIG_FILE, LOG_FILE
from .utils.logger import setup_logger


def main() -> None:
    """
    Main entry point for the application.

    This function:
    1. Sets up logging
    2. Initializes configuration
    3. Creates and shows the main window
    """
    # Set up logging
    logger = setup_logger(log_file=LOG_FILE)
    logger.info("Starting Jellyfin Music Organizer")

    try:
        # Initialize configuration
        config = ConfigManager(CONFIG_FILE)
        config.load()

        # Create Qt application
        app = QApplication(sys.argv)

        # Create and show main window
        window = MusicOrganizer()
        window.show()

        # Start event loop
        sys.exit(app.exec_())

    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

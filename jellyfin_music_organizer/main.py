"""
Main entry point for the Jellyfin Music Organizer application.
"""

import sys
from logging import Logger
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox

from .ui.music_organizer import MusicOrganizer
from .utils.config import ConfigManager
from .utils.logger import setup_logger
from .utils.platform_utils import PlatformPaths, platform


def main() -> None:
    """Main entry point with proper platform initialization."""
    logger: Optional[Logger] = None

    try:
        # Set up logging with platform-specific paths
        log_path = PlatformPaths.get_app_data_dir() / "logs" / "app.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        logger = setup_logger(log_file=log_path)
        logger.info("Starting Jellyfin Music Organizer")

        # Initialize configuration with platform-specific paths
        config_path = PlatformPaths.get_app_data_dir() / "config.json"
        config = ConfigManager(config_path)
        config.load()

        # Set up platform-specific UI settings
        app = QApplication(sys.argv)
        if platform.system() == "Windows":
            app.setAttribute(Qt.AA_EnableHighDpiScaling)
            app.setAttribute(Qt.AA_UseHighDpiPixmaps)

        window = MusicOrganizer()
        window.show()

        sys.exit(app.exec_())
    except Exception as e:
        error_msg = f"Application error: {str(e)}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        QMessageBox.critical(None, "Error", error_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()

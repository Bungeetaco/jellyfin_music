"""
Logging configuration for the Jellyfin Music Organizer application.
"""

import logging
import logging.handlers
import sys
from typing import Any, Dict, Optional
from pathlib import Path


class LoggerConfig:
    """Logger configuration with proper typing."""

    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DEFAULT_LEVEL = logging.INFO

    @staticmethod
    def setup_logger(
        name: Optional[str] = None,
        log_file: Optional[str] = None,
        level: int = DEFAULT_LEVEL,
        format_str: str = DEFAULT_FORMAT,
        max_bytes: int = 1024 * 1024,  # 1MB
        backup_count: int = 5,
    ) -> logging.Logger:
        """Set up a logger with file and console handlers."""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Create formatters and handlers
        formatter = logging.Formatter(format_str)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (if log_file specified)
        if log_file:
            try:
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file, maxBytes=max_bytes, backupCount=backup_count
                )
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.error(f"Failed to set up file handler: {e}")

        return logger

    @staticmethod
    def get_log_config() -> Dict[str, Any]:
        """Get logging configuration dictionary."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {"format": LoggerConfig.DEFAULT_FORMAT},
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": sys.stdout,
                },
            },
            "loggers": {
                "": {  # Root logger
                    "handlers": ["console"],
                    "level": LoggerConfig.DEFAULT_LEVEL,
                    "propagate": True,
                }
            },
        }

def setup_logger(name: str = "jellyfin_music_organizer", log_file: Optional[Path] = None) -> logging.Logger:
    """Set up and configure logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Add file handler if log_file is specified
        if log_file:
            file_handler = logging.FileHandler(str(log_file))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger

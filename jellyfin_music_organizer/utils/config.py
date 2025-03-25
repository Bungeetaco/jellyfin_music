"""
Configuration management for the Jellyfin Music Organizer application.
"""

import json
import platform
from pathlib import Path
from typing import Any, Dict, Optional
import logging

from .platform_utils import PlatformPaths


class ConfigManager:
    """
    Manages application configuration.

    This class:
    1. Handles loading and saving settings
    2. Provides default values
    3. Validates configuration
    """

    DEFAULT_CONFIG: Dict[str, Any] = {
        "music_folder_path": "",
        "destination_folder_path": "",
        "mute_sound": False,
        "version": "3.06",
        "window_state": {},
        "platform_specific": {},
    }

    def __init__(self, config_path: Optional[str] = None) -> None:
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.settings: Dict[str, Any] = {}

    def _get_platform_defaults(self) -> Dict[str, Any]:
        """Get platform-specific default settings."""
        system = platform.system().lower()
        if system == "windows":
            return {"use_native_dialogs": False, "dpi_scaling": True}
        elif system == "darwin":
            return {"use_native_dialogs": True, "use_native_titlebar": True}
        else:  # Linux
            return {"use_native_dialogs": True, "style": "fusion"}

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration values."""
        try:
            required_keys = {"music_folder_path", "destination_folder_path", "version"}
            if not all(key in config for key in required_keys):
                return False

            if not isinstance(config.get("mute_sound"), bool):
                return False

            return True
        except Exception as e:
            self.logger.error(f"Config validation failed: {e}")
            return False

    def load(self) -> Dict[str, Any]:
        """Load configuration with validation."""
        try:
            if self.config_path and Path(self.config_path).exists():
                with open(self.config_path, "r") as f:
                    loaded_config = json.load(f)
                    if self.validate_config(loaded_config):
                        self.settings.update(loaded_config)
                    else:
                        self.logger.warning("Invalid configuration, using defaults")
            return self.settings
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return self.settings

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self.settings, f, indent=4)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        if key in self.DEFAULT_CONFIG:
            self.settings[key] = value
        else:
            self.logger.warning(f"Attempted to set unknown configuration key: {key}")

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.settings = self.DEFAULT_CONFIG.copy()
        self.save()

    def get_log_path(self) -> Path:
        """Get platform-specific log file path."""
        try:
            log_dir = PlatformPaths.get_app_data_dir() / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            return log_dir / "app.log"
        except Exception as e:
            self.logger.error(f"Failed to get log path: {e}")
            raise

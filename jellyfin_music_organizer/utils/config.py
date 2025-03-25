"""
Configuration management for the Jellyfin Music Organizer application.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional


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
    }

    def __init__(self, config_path: str = "settings_jmo.json") -> None:
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.logger = logging.getLogger(__name__)

    def load(self) -> None:
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    loaded_config = json.load(f)
                    # Update only valid keys
                    for key in self.DEFAULT_CONFIG:
                        if key in loaded_config:
                            self.config[key] = loaded_config[key]
                self.logger.info("Configuration loaded successfully")
            else:
                self.logger.info("No configuration file found, using defaults")
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            # Keep default configuration on error

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=4)
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
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        if key in self.DEFAULT_CONFIG:
            self.config[key] = value
        else:
            self.logger.warning(f"Attempted to set unknown configuration key: {key}")

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()

"""
Configuration management for the Jellyfin Music Organizer.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class AppConfig:
    """Application configuration data structure."""

    music_folder_path: str = ""
    destination_folder_path: str = ""
    version: str = "3.06"


class ConfigManager:
    """Manages application configuration and settings."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the configuration manager.

        Args:
            config_path: Optional path to the configuration file.
                        If None, uses default location in user's home directory.
        """
        self.config_path = config_path or Path.home() / ".jellyfin_music_organizer" / "config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = AppConfig()

    def load(self) -> None:
        """Load configuration from file if it exists."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    self.config = AppConfig(**data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading config: {e}")

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config.__dict__, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str) -> Any:
        """Get a configuration value."""
        return getattr(self.config, key, None)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save()

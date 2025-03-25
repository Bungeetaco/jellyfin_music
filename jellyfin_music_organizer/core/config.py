"""
Configuration management for the Jellyfin Music Organizer.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class AppConfig:
    """Application configuration data structure."""
    music_folder_path: str = ""
    destination_folder_path: str = ""
    mute_sound: bool = False
    version: str = "3.06"
    remove_illegal_chars: bool = True
    window_state: Dict[str, Any] = None

class ConfigManager:
    """Manages application configuration and settings."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration manager with path validation."""
        try:
            self.config_path = self._validate_config_path(config_path)
            self.config = AppConfig()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            logger.error(f"Failed to initialize config manager: {e}")
            raise

    def _validate_config_path(self, config_path: Optional[Path]) -> Path:
        """Validate and prepare configuration path.
        
        Args:
            config_path: Optional configuration file path
            
        Returns:
            Validated Path object
        """
        try:
            path = config_path or Path.home() / ".jellyfin_music_organizer" / "config.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
        except Exception as e:
            logger.error(f"Failed to validate config path: {e}")
            raise ValueError(f"Invalid configuration path: {e}")

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
        """Save current configuration to file with backup."""
        backup_path = self.config_path.with_suffix('.json.bak')
        try:
            # Create backup of existing config
            if self.config_path.exists():
                self.config_path.rename(backup_path)

            # Save new config
            with open(self.config_path, "w", encoding='utf-8') as f:
                json.dump(self.config.__dict__, f, indent=4, ensure_ascii=False)

            # Remove backup on successful save
            if backup_path.exists():
                backup_path.unlink()

            logger.debug("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            # Restore backup if save failed
            if backup_path.exists():
                backup_path.rename(self.config_path)
            raise

    def get(self, key: str) -> Any:
        """Get a configuration value."""
        return getattr(self.config, key, None)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save()

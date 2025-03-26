import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests  # type: ignore[import-untyped]


@dataclass
class Version:
    """Version information."""

    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version_str: str) -> "Version":
        """Create version from string."""
        major, minor, patch = map(int, version_str.split("."))
        return cls(major, minor, patch)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: "Version") -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)


class UpdateManager:
    """Manage application updates."""

    def __init__(self, current_version: str, update_url: str, app_path: Path) -> None:
        self.logger = logging.getLogger(__name__)
        self.current_version = Version.from_string(current_version)
        self.update_url = update_url
        self.app_path = app_path

    def check_for_updates(self) -> Optional[Version]:
        """Check for available updates."""
        try:
            response = requests.get(self.update_url, timeout=10)
            response.raise_for_status()

            data = response.json()
            latest_version = Version.from_string(data["version"])

            if latest_version > self.current_version:
                return latest_version
            return None
        except Exception as e:
            self.logger.error(f"Failed to check for updates: {e}")
            return None

    def download_update(self, version: Version) -> Optional[Path]:
        """Download update package."""
        try:
            download_url = f"{self.update_url}/download/{version}"
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            update_file = self.app_path / f"update_{version}.zip"
            with open(update_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return update_file
        except Exception as e:
            self.logger.error(f"Failed to download update: {e}")
            return None

    def install_update(self, update_file: Path) -> bool:
        """Install downloaded update."""
        try:
            # Start update script in new process
            update_script = self.app_path / "update_script.py"
            subprocess.Popen(
                [sys.executable, str(update_script), str(update_file), str(self.app_path)]
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to install update: {e}")
            return False

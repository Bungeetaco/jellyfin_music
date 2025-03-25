import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Migration:
    """Database migration."""

    version: int
    description: str
    up: Callable[[Dict[str, Any]], None]
    down: Callable[[Dict[str, Any]], None]


class MigrationManager:
    """Manage database migrations."""

    def __init__(self, db_path: Path) -> None:
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        self._migrations: List[Migration] = []
        self._current_version = 0

    def register_migration(
        self,
        version: int,
        description: str,
        up: Callable[[Dict[str, Any]], None],
        down: Callable[[Dict[str, Any]], None],
    ) -> None:
        """Register a new migration."""
        migration = Migration(version, description, up, down)
        self._migrations.append(migration)
        self._migrations.sort(key=lambda m: m.version)

    def get_current_version(self) -> int:
        """Get current database version.
        
        Returns:
            int: Current database version number, defaults to 0 if not found
        """
        try:
            if not self.db_path.exists():
                return 0

            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                version = data.get("version", 0)
                # Ensure we return an integer
                if not isinstance(version, int):
                    self.logger.warning(f"Invalid version type in database: {type(version)}")
                    return 0
                return version
        except Exception as e:
            self.logger.error(f"Failed to get current version: {e}")
            return 0

    def migrate(self, target_version: Optional[int] = None) -> bool:
        """Run migrations to target version."""
        try:
            current = self.get_current_version()
            target = target_version or self._migrations[-1].version

            # Load current data
            data: Dict[str, Any] = {}
            if self.db_path.exists():
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

            if target > current:
                # Migrate up
                for migration in self._migrations:
                    if current < migration.version <= target:
                        self.logger.info(
                            f"Running migration {migration.version}: {migration.description}"
                        )
                        migration.up(data)
                        data["version"] = migration.version
            else:
                # Migrate down
                for migration in reversed(self._migrations):
                    if target < migration.version <= current:
                        self.logger.info(f"Rolling back migration {migration.version}")
                        migration.down(data)
                        data["version"] = migration.version - 1

            # Save updated data
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            return False

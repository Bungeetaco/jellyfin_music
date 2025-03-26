import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Dict, Optional, Protocol, Type, TypeVar

T = TypeVar("T")


class Plugin(Protocol):
    """Base protocol for plugins."""

    name: str
    version: str

    def initialize(self) -> None: ...
    def cleanup(self) -> None: ...


class PluginManager:
    """Manage application plugins."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_paths: Dict[str, Path] = {}

    def register_plugin(self, plugin_class: Type[Plugin], name: Optional[str] = None) -> bool:
        """Register a plugin class."""
        try:
            plugin_name = name or plugin_class.name
            plugin = plugin_class()
            plugin.initialize()
            self._plugins[plugin_name] = plugin
            return True
        except Exception as e:
            self.logger.error(f"Failed to register plugin {name}: {e}")
            return False

    def load_plugins(self, plugin_dir: Path) -> None:
        """Load plugins from directory."""
        try:
            for file_path in plugin_dir.glob("*.py"):
                if file_path.stem.startswith("_"):
                    continue

                try:
                    spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        # Look for plugin class in module
                        for item_name in dir(module):
                            item = getattr(module, item_name)
                            if (
                                isinstance(item, type)
                                and hasattr(item, "name")
                                and hasattr(item, "version")
                            ):
                                self.register_plugin(item)
                except Exception as e:
                    self.logger.error(f"Failed to load plugin {file_path}: {e}")

        except Exception as e:
            self.logger.error(f"Failed to load plugins from {plugin_dir}: {e}")

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def cleanup(self) -> None:
        """Clean up all plugins."""
        for plugin in self._plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                self.logger.error(f"Failed to cleanup plugin {plugin.name}: {e}")
        self._plugins.clear()

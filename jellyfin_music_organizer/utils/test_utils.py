from typing import Any, Dict, Optional, Type, TypeVar
from pathlib import Path
import tempfile
import shutil
import contextlib
from unittest.mock import MagicMock

T = TypeVar('T')

class TestUtils:
    """Utilities for testing with proper type safety."""

    @staticmethod
    @contextlib.contextmanager
    def temp_directory() -> Path:
        """Create a temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            yield temp_dir
        finally:
            shutil.rmtree(temp_dir)

    @staticmethod
    def create_mock_widget(widget_class: Type[T]) -> MagicMock:
        """Create a mock widget with common attributes."""
        mock = MagicMock(spec=widget_class)
        mock.windowTitle.return_value = "Test Window"
        mock.isVisible.return_value = True
        return mock

    @staticmethod
    def create_test_config(
        base_path: Path,
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a test configuration."""
        config = {
            "music_folder_path": str(base_path / "music"),
            "destination_folder_path": str(base_path / "organized"),
            "mute_sound": True,
            "version": "test",
            "window_state": {},
            "platform_specific": {"use_native_dialogs": False}
        }
        if settings:
            config.update(settings)
        return config 
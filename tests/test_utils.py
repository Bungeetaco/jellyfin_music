"""
Unit tests for the Jellyfin Music Organizer utility modules.

This module provides comprehensive testing for core utilities including:
- Configuration management
- Resource handling
- Progress tracking
- Thread management
- Test utilities
"""

import contextlib
import os
import platform
import shutil
import tempfile
import threading
import time
import unittest
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Type, TypeVar
from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtWidgets import QWidget

from jellyfin_music_organizer.utils.config import ConfigManager
from jellyfin_music_organizer.utils.exceptions import FileOperationError
from jellyfin_music_organizer.utils.progress import ProgressInfo, ProgressTracker
from jellyfin_music_organizer.utils.resources import ResourceManager
from jellyfin_music_organizer.utils.threads import ThreadManager

T = TypeVar("T")


class TestUtils:
    """Utilities for testing with proper type safety."""

    @staticmethod
    @contextlib.contextmanager
    def temp_directory() -> Generator[Path, None, None]:
        """Create a temporary directory for testing.

        Yields:
            Path: A temporary directory path that will be cleaned up after use

        Raises:
            OSError: If directory creation or cleanup fails
        """
        temp_dir = Path(tempfile.mkdtemp())
        try:
            yield temp_dir
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    @staticmethod
    def create_mock_widget(widget_class: Type[T]) -> MagicMock:
        """Create a mock widget with common attributes.

        Args:
            widget_class: The widget class to mock

        Returns:
            MagicMock: Configured mock widget
        """
        mock = MagicMock(spec=widget_class)
        mock.windowTitle.return_value = "Test Window"
        mock.isVisible.return_value = True
        mock.size().width.return_value = 800
        mock.size().height.return_value = 600
        return mock

    @staticmethod
    def create_test_config(
        base_path: Path, settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a test configuration.

        Args:
            base_path: Base path for configuration
            settings: Optional additional settings

        Returns:
            Dict[str, Any]: Test configuration
        """
        config = {
            "music_folder_path": str(base_path / "music"),
            "destination_folder_path": str(base_path / "organized"),
            "mute_sound": True,
            "version": "test",
            "window_state": {},
            "platform_specific": {
                "use_native_dialogs": False,
                "dpi_scaling": True,
                "style": "fusion",
            },
        }
        if settings:
            config.update(settings)
        return config


@pytest.mark.usefixtures("temp_dir")
class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        self.config = ConfigManager(self.config_path)

    def tearDown(self) -> None:
        """Clean up test environment."""
        if self.config_path.exists():
            self.config_path.unlink()
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_default_config(self) -> None:
        """Test default configuration values."""
        self.assertEqual(self.config.get("music_folder_path"), "")
        self.assertEqual(self.config.get("destination_folder_path"), "")
        self.assertFalse(self.config.get("mute_sound"))
        self.assertIsInstance(self.config.get("platform_specific"), dict)

    def test_save_load(self) -> None:
        """Test saving and loading configuration."""
        test_path = "/test/path"
        self.config.set("music_folder_path", test_path)
        self.config.save()

        new_config = ConfigManager(self.config_path)
        new_config.load()
        self.assertEqual(new_config.get("music_folder_path"), test_path)

    def test_invalid_key(self) -> None:
        """Test setting invalid configuration key."""
        self.config.set("invalid_key", "value")
        self.assertIsNone(self.config.get("invalid_key"))

    def test_platform_specific_config(self) -> None:
        """Test platform-specific configuration."""
        system = platform.system().lower()
        self.config.load()
        platform_config = self.config.get("platform_specific", {})
        
        if system == "windows":
            self.assertFalse(platform_config.get("use_native_dialogs"))
        elif system == "darwin":
            self.assertTrue(platform_config.get("use_native_dialogs"))
        else:  # Linux
            self.assertTrue(platform_config.get("use_native_dialogs"))


class TestResourceManager(unittest.TestCase):
    """Test cases for ResourceManager."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.resource_dir = Path(self.temp_dir) / "resources"
        self.resource_dir.mkdir()
        self.resource_manager = ResourceManager(self.temp_dir)

        # Create test resources
        self.test_file = self.resource_dir / "test.txt"
        self.test_file.write_text("test content")
        self.binary_file = self.resource_dir / "test.bin"
        self.binary_file.write_bytes(b"\x00\x01\x02\x03")

    def tearDown(self) -> None:
        """Clean up test environment."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_register_resource(self) -> None:
        """Test resource registration."""
        self.resource_manager.register_resource("test", "resources/test.txt")
        self.assertEqual(
            self.resource_manager.get_resource_path("test"),
            self.test_file
        )

    def test_get_resource_content(self) -> None:
        """Test getting resource content."""
        self.resource_manager.register_resource("test", "resources/test.txt")
        content = self.resource_manager.get_resource_content("test")
        self.assertEqual(content, b"test content")

    def test_get_binary_content(self) -> None:
        """Test getting binary resource content."""
        self.resource_manager.register_resource("binary", "resources/test.bin")
        content = self.resource_manager.get_resource_content("binary")
        self.assertEqual(content, b"\x00\x01\x02\x03")

    def test_invalid_resource(self) -> None:
        """Test accessing invalid resource."""
        with self.assertRaises(FileOperationError):
            self.resource_manager.get_resource_path("invalid")

    def test_resource_validation(self) -> None:
        """Test resource validation."""
        self.resource_manager.register_resource("test", "resources/test.txt")
        self.assertTrue(self.resource_manager.validate_resources())
        
        # Test with missing resource
        self.test_file.unlink()
        self.assertFalse(self.resource_manager.validate_resources())


class TestProgressTracker(unittest.TestCase):
    """Test cases for ProgressTracker."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.tracker = ProgressTracker(100)

    def test_initial_state(self) -> None:
        """Test initial progress state."""
        self.assertEqual(self.tracker.current, 0)
        self.assertEqual(self.tracker.total, 100)
        self.assertEqual(self.tracker.status, "")
        self.assertIsNone(self.tracker.current_item)

    def test_progress_update(self) -> None:
        """Test progress updates."""
        self.tracker.update(50, "test_item", "Processing...")
        self.assertEqual(self.tracker.current, 50)
        self.assertEqual(self.tracker.current_item, "test_item")
        self.assertEqual(self.tracker.status, "Processing...")

    def test_percentage_calculation(self) -> None:
        """Test percentage calculation."""
        test_cases = [
            (0, 0.0),
            (50, 50.0),
            (100, 100.0),
        ]
        for progress, expected in test_cases:
            with self.subTest(progress=progress):
                self.tracker.update(progress)
                self.assertEqual(self.tracker.get_percentage(), expected)

    def test_time_estimation(self) -> None:
        """Test time estimation."""
        self.tracker.update(1, "test_item", "Starting...")
        time.sleep(0.1)
        self.tracker.update(50)
        remaining = self.tracker.get_estimated_time_remaining()
        self.assertIsNotNone(remaining)
        self.assertGreater(remaining, 0)

    def test_edge_cases(self) -> None:
        """Test edge cases and boundary conditions."""
        # Test zero total
        zero_tracker = ProgressTracker(0)
        self.assertEqual(zero_tracker.get_percentage(), 0.0)
        self.assertIsNone(zero_tracker.get_estimated_time_remaining())

        # Test maximum value
        self.tracker.update(100)
        self.assertEqual(self.tracker.get_percentage(), 100.0)

    def test_invalid_updates(self) -> None:
        """Test handling of invalid progress updates."""
        with self.assertRaises(ValueError):
            self.tracker.update(-1)
        with self.assertRaises(ValueError):
            self.tracker.update(101)

    def test_progress_callback(self) -> None:
        """Test progress callback functionality."""
        callback_called = False
        progress_info = None

        def callback(info: ProgressInfo) -> None:
            nonlocal callback_called, progress_info
            callback_called = True
            progress_info = info

        tracker = ProgressTracker(100, callback)
        tracker.update(50, "test", "Testing...")

        self.assertTrue(callback_called)
        self.assertIsNotNone(progress_info)
        self.assertEqual(progress_info.current, 50)
        self.assertEqual(progress_info.status, "Testing...")


class TestThreadManager(unittest.TestCase):
    """Test cases for ThreadManager."""

    def setUp(self) -> None:
        """Set up test environment."""
        self.thread_manager = ThreadManager()

    def tearDown(self) -> None:
        """Clean up test environment."""
        self.thread_manager.stop_all_threads()

    def test_thread_lifecycle(self) -> None:
        """Test thread creation and cleanup."""
        event = threading.Event()

        def test_function() -> None:
            event.wait(1.0)

        self.thread_manager.start_thread("test", test_function)
        time.sleep(0.1)

        try:
            self.assertTrue(self.thread_manager.is_thread_running("test"))
            event.set()
            time.sleep(0.1)
            self.assertFalse(self.thread_manager.is_thread_running("test"))
        finally:
            event.set()
            self.thread_manager.stop_thread("test")

    def test_thread_error_handling(self) -> None:
        """Test thread error handling."""
        def error_function() -> None:
            raise ValueError("Test error")

        self.thread_manager.start_thread("error", error_function)
        message = self.thread_manager.get_thread_message("error", timeout=1.0)
        self.assertIsNotNone(message)
        self.assertEqual(message[0], "error")
        self.assertIn("Test error", message[1])

    def test_concurrent_threads(self) -> None:
        """Test handling of multiple concurrent threads."""
        events = [threading.Event() for _ in range(3)]
        results = []

        def thread_function(event: threading.Event, index: int) -> None:
            event.wait(1.0)
            results.append(index)

        # Start multiple threads
        for i, event in enumerate(events):
            self.thread_manager.start_thread(
                f"thread_{i}",
                thread_function,
                args=(event, i)
            )

        # Verify all threads are running
        for i in range(3):
            self.assertTrue(
                self.thread_manager.is_thread_running(f"thread_{i}")
            )

        # Allow threads to complete
        for event in events:
            event.set()

        time.sleep(0.2)  # Give threads time to finish

        # Verify all threads completed
        for i in range(3):
            self.assertFalse(
                self.thread_manager.is_thread_running(f"thread_{i}")
            )

        # Verify results
        self.assertEqual(sorted(results), [0, 1, 2])

    def test_thread_cleanup(self) -> None:
        """Test proper thread cleanup."""
        self.thread_manager.start_thread(
            "test",
            lambda: time.sleep(0.1)
        )
        time.sleep(0.2)  # Let thread complete naturally
        self.assertFalse(self.thread_manager.is_thread_running("test"))
        self.assertNotIn("test", self.thread_manager.active_threads)

    @patch("logging.Logger.error")
    def test_thread_exception_logging(self, mock_error: MagicMock) -> None:
        """Test exception logging in threads."""
        def raising_function() -> None:
            raise RuntimeError("Test exception")

        self.thread_manager.start_thread("error_thread", raising_function)
        time.sleep(0.1)  # Give thread time to raise exception
        mock_error.assert_called()
        self.assertIn("Test exception", str(mock_error.call_args))


if __name__ == "__main__":
    unittest.main()

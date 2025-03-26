"""
Unit tests for the Jellyfin Music Organizer utility modules.
"""

import os
import tempfile
import time
import unittest
from pathlib import Path

from jellyfin_music_organizer.utils.config import ConfigManager
from jellyfin_music_organizer.utils.exceptions import FileOperationError
from jellyfin_music_organizer.utils.progress import ProgressTracker
from jellyfin_music_organizer.utils.resources import ResourceManager
from jellyfin_music_organizer.utils.threads import ThreadManager


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
        self.config = ConfigManager(self.config_path)

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        os.rmdir(self.temp_dir)

    def test_default_config(self):
        """Test default configuration values."""
        self.assertEqual(self.config.get("music_folder_path"), "")
        self.assertEqual(self.config.get("destination_folder_path"), "")
        self.assertFalse(self.config.get("mute_sound"))

    def test_save_load(self):
        """Test saving and loading configuration."""
        self.config.set("music_folder_path", "/test/path")
        self.config.save()

        new_config = ConfigManager(self.config_path)
        new_config.load()
        self.assertEqual(new_config.get("music_folder_path"), "/test/path")

    def test_invalid_key(self):
        """Test setting invalid configuration key."""
        self.config.set("invalid_key", "value")
        self.assertIsNone(self.config.get("invalid_key"))


class TestResourceManager(unittest.TestCase):
    """Test cases for ResourceManager."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.resource_dir = os.path.join(self.temp_dir, "resources")
        os.makedirs(self.resource_dir)
        self.resource_manager = ResourceManager(self.temp_dir)

        # Create test resource
        self.test_file = os.path.join(self.resource_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("test content")

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_register_resource(self):
        """Test resource registration."""
        self.resource_manager.register_resource("test", "resources/test.txt")
        self.assertEqual(self.resource_manager.get_resource_path("test"), Path(self.test_file))

    def test_get_resource_content(self):
        """Test getting resource content."""
        self.resource_manager.register_resource("test", "resources/test.txt")
        content = self.resource_manager.get_resource_content("test")
        self.assertEqual(content, b"test content")

    def test_invalid_resource(self):
        """Test accessing invalid resource."""
        with self.assertRaises(FileOperationError):
            self.resource_manager.get_resource_path("invalid")


class TestProgressTracker(unittest.TestCase):
    """Test cases for ProgressTracker."""

    def setUp(self):
        """Set up test environment."""
        self.tracker = ProgressTracker(100)

    def test_initial_state(self):
        """Test initial progress state."""
        self.assertEqual(self.tracker.current, 0)
        self.assertEqual(self.tracker.total, 100)
        self.assertEqual(self.tracker.status, "Starting...")

    def test_progress_update(self):
        """Test progress updates."""
        self.tracker.update(50, "test_item", "Processing...")
        self.assertEqual(self.tracker.current, 50)
        self.assertEqual(self.tracker.current_item, "test_item")
        self.assertEqual(self.tracker.status, "Processing...")

    def test_percentage_calculation(self):
        """Test percentage calculation."""
        self.tracker.update(75)
        self.assertEqual(self.tracker.get_percentage(), 75.0)

    def test_time_estimation(self):
        """Test time estimation."""
        self.tracker.update(50)
        remaining = self.tracker.get_estimated_time_remaining()
        self.assertIsNotNone(remaining)
        self.assertGreater(remaining, 0)


class TestThreadManager(unittest.TestCase):
    """Test cases for ThreadManager."""

    def setUp(self):
        """Set up test environment."""
        self.thread_manager = ThreadManager()

    def test_thread_lifecycle(self):
        """Test thread creation and cleanup."""

        def test_function():
            time.sleep(0.1)  # Add a small delay to ensure thread is running

        self.thread_manager.start_thread("test", test_function)
        time.sleep(0.2)  # Give thread time to start
        self.assertTrue(self.thread_manager.is_thread_running("test"))
        time.sleep(0.2)  # Give thread time to complete
        self.assertFalse(self.thread_manager.is_thread_running("test"))

    def test_thread_error_handling(self):
        """Test thread error handling."""

        def error_function():
            raise ValueError("Test error")

        self.thread_manager.start_thread("error", error_function)
        message = self.thread_manager.get_thread_message("error", timeout=1.0)
        self.assertIsNotNone(message)
        self.assertEqual(message[0], "error")
        self.assertIn("Test error", message[1])


if __name__ == "__main__":
    unittest.main()

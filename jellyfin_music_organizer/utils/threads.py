"""
Thread management for the Jellyfin Music Organizer application.
"""

import threading
from logging import getLogger
from pathlib import Path
from queue import Queue
from typing import Any, Callable, Dict, Optional, Tuple, cast

from PyQt5.QtCore import QThread, QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

from .logger import setup_logger
from .qt_types import QtConstants

logger = getLogger(__name__)


class ThreadManager:
    """
    Manages application threads.

    This class:
    1. Tracks active threads
    2. Provides thread cleanup
    3. Manages thread communication
    """

    def __init__(self) -> None:
        """Initialize the thread manager."""
        self.active_threads: Dict[str, threading.Thread] = {}
        self.message_queues: Dict[str, Queue] = {}
        self.logger = setup_logger()

    def start_thread(
        self, name: str, target: Callable, args: tuple = (), kwargs: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Start a new thread.

        Args:
            name: Thread name
            target: Target function to run
            args: Positional arguments for target
            kwargs: Keyword arguments for target
        """
        if name in self.active_threads and self.active_threads[name].is_alive():
            self.logger.warning(f"Thread {name} is already running")
            return

        if kwargs is None:
            kwargs = {}

        thread = threading.Thread(
            target=self._thread_wrapper, name=name, args=(name, target, args, kwargs)
        )
        thread.daemon = True
        self.active_threads[name] = thread
        self.message_queues[name] = Queue()
        thread.start()

    def _thread_wrapper(
        self, name: str, target: Callable, args: tuple, kwargs: Dict[str, Any]
    ) -> None:
        """
        Wrapper function for thread execution.

        Args:
            name: Thread name
            target: Target function to run
            args: Positional arguments for target
            kwargs: Keyword arguments for target
        """
        try:
            target(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error in thread {name}: {e}")
            self.message_queues[name].put(("error", str(e)))
        finally:
            self.message_queues[name].put(("complete", None))

    def stop_thread(self, name: str) -> None:
        """
        Stop a running thread.

        Args:
            name: Thread name
        """
        if name in self.active_threads:
            thread = self.active_threads[name]
            if thread.is_alive():
                thread.join(timeout=1.0)
            del self.active_threads[name]
            del self.message_queues[name]

    def stop_all_threads(self) -> None:
        """Stop all running threads."""
        for name in list(self.active_threads.keys()):
            self.stop_thread(name)

    def get_thread_status(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a thread.

        Args:
            name: Thread name

        Returns:
            Dictionary containing thread status, or None if thread doesn't exist
        """
        if name not in self.active_threads:
            return None

        thread = self.active_threads[name]
        return {
            "name": thread.name,
            "alive": thread.is_alive(),
            "daemon": thread.daemon,
            "ident": thread.ident,
        }

    def get_thread_message(self, name: str, timeout: float = 0.1) -> Optional[tuple]:
        """
        Get a message from a thread's queue.

        Args:
            name: Thread name
            timeout: Timeout in seconds

        Returns:
            Tuple of (message_type, message_data), or None if no message
        """
        if name not in self.message_queues:
            return None

        try:
            return self.message_queues[name].get(timeout=timeout)
        except Exception:
            return None

    def is_thread_running(self, name: str) -> bool:
        """
        Check if a thread is running.

        Args:
            name: Thread name

        Returns:
            True if thread is running, False otherwise
        """
        return name in self.active_threads and self.active_threads[name].is_alive()


class BaseThread(QThread):
    """Base thread class with proper typing."""

    error_signal = pyqtSignal(str)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs: Dict[str, Any] = kwargs
        self.is_running: bool = True

    def get_args(self) -> Optional[Tuple[Any, ...]]:
        """Get thread arguments safely."""
        try:
            return tuple(self.kwargs.values()) if self.kwargs else None
        except Exception as e:
            self.error_signal.emit(f"Failed to get arguments: {e}")
            return None


class NotificationAudioThread(BaseThread):
    """Thread for handling audio notifications."""

    media_status_changed = pyqtSignal(int)

    def __init__(self, audio_file: str) -> None:
        super().__init__(audio_file=audio_file)
        self._player: Optional[QMediaPlayer] = None

    def on_media_status_changed(self, status: int) -> None:
        """Handle media status changes."""
        self.media_status_changed.emit(status)
        if status == QtConstants.EndOfMedia:
            self.is_running = False

    def run(self) -> None:
        """Run the notification thread with proper cleanup."""
        try:
            self._player = QMediaPlayer()
            self._player.setMedia(self._get_media_content())
            self._player.mediaStatusChanged.connect(self.on_media_status_changed)
            self._player.error.connect(self._handle_player_error)

            self._player.play()

            # Wait for playback to complete
            while self._player and self._player.state() == QMediaPlayer.State.PlayingState:
                self.msleep(100)

        except Exception as e:
            logger.error(f"Audio notification error: {e}")
            self.error_signal.emit(f"Audio playback failed: {str(e)}")
        finally:
            self._cleanup()

    def _get_media_content(self) -> QMediaContent:
        """Get media content with resource validation.

        Returns:
            QMediaContent object for the audio file

        Raises:
            RuntimeError: If audio file not found
        """
        resource_path = f":/sounds/{self.kwargs['audio_file']}.wav"
        if not Path(resource_path).exists():
            logger.error(f"Audio file not found: {resource_path}")
            raise RuntimeError(f"Audio file not found: {self.kwargs['audio_file']}")

        return QMediaContent(QUrl.fromLocalFile(resource_path))

    def _handle_player_error(self) -> None:
        """Handle player errors."""
        if self._player:
            error_msg = self._player.errorString()
            self.error_signal.emit(f"Player error: {error_msg}")

    def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self._player:
                self._player.stop()
                self._player.deleteLater()
                self._player = None
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def stop(self) -> None:
        """Stop the notification thread safely."""
        self.quit()
        self._cleanup()

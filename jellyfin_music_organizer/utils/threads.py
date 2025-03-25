"""
Thread management for the Jellyfin Music Organizer application.
"""

import threading
from logging import getLogger
from pathlib import Path
from queue import Queue
from typing import Any, Callable, Dict, Optional

from PyQt5.QtCore import QThread, QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

from .logger import setup_logger

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
        self, name: str, target: Callable, args: tuple = (), kwargs: Dict[str, Any] = None
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


class NotificationAudioThread(QThread):
    """Thread for playing notification sounds."""

    kill_thread_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, audio_file_name: str) -> None:
        """Initialize notification thread with resource validation.

        Args:
            audio_file_name: Name of the audio file to play
        """
        super().__init__()
        self.audio_file_name = audio_file_name
        self.player: Optional[QMediaPlayer] = None
        self.is_running = True

    def run(self) -> None:
        """Run the notification thread with proper cleanup."""
        try:
            self.player = QMediaPlayer()
            self.player.setMedia(self._get_media_content())
            self.player.mediaStatusChanged.connect(self.on_media_status_changed)
            self.player.error.connect(self._handle_player_error)

            self.player.play()

            # Wait for playback to complete
            while self.is_running and self.player.state() == QMediaPlayer.PlayingState:
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
        resource_path = f":/sounds/{self.audio_file_name}.wav"
        if not Path(resource_path).exists():
            logger.error(f"Audio file not found: {resource_path}")
            raise RuntimeError(f"Audio file not found: {self.audio_file_name}")

        return QMediaContent(QUrl.fromLocalFile(resource_path))

    def _handle_player_error(self, error: QMediaPlayer.Error) -> None:
        """Handle media player errors.

        Args:
            error: Media player error code
        """
        error_msg = f"Media player error: {self.player.errorString()}"
        logger.error(error_msg)
        self.error_signal.emit(error_msg)
        self.stop()

    def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.player:
                self.player.stop()
                self.player.deleteLater()
                self.player = None
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    def stop(self) -> None:
        """Stop the notification thread safely."""
        self.is_running = False
        self._cleanup()

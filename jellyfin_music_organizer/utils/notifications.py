"""Platform-independent notification handling."""

import logging
import platform
import sys
from abc import ABC, abstractmethod
from typing import Optional

from PyQt5.QtCore import QObject, QUrl, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

from .notification_config import NotificationConfig
from .platform_utils import PlatformPaths
from .qt_types import QtMediaConstants

logger = logging.getLogger(__name__)

if sys.platform == "win32":
    pass

    # Windows constants
    MB_OK = 0x00000000
    MB_ICONHAND = 0x00000010
    MB_ICONASTERISK = 0x00000040
    SND_ALIAS = 0x00010000


class NotificationStrategy(ABC):
    """Abstract base class for platform-specific notifications."""

    @abstractmethod
    def play_sound(self, sound_name: str) -> bool:
        """Play notification sound."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if notification system is available."""

    @abstractmethod
    def show_message(self, title: str, message: str, icon_type: int = 0) -> bool:
        """Show notification message."""


class WindowsNotificationStrategy(NotificationStrategy):
    """Windows-specific notification implementation."""

    def __init__(self) -> None:
        if sys.platform == "win32":
            import winreg
            import winsound

            self.winsound = winsound
            self.winreg = winreg
        else:
            self.winsound = None
            self.winreg = None

    def play_sound(self, sound_name: str) -> bool:
        if not self.winsound:
            return False
        try:
            self.winsound.PlaySound(sound_name, self.winsound.SND_ALIAS)
            return True
        except Exception:
            return False

    def is_available(self) -> bool:
        if not (self.winsound and self.winreg):
            return False
        try:
            self.winreg.OpenKey(self.winreg.HKEY_CURRENT_USER, r"AppEvents\Schemes")
            return True
        except Exception:
            return False

    def show_message(self, title: str, message: str, icon_type: int = 0) -> bool:
        try:
            from win32gui import MessageBeep

            MessageBeep(icon_type)
            return True
        except Exception:
            return False


class MacNotificationStrategy(NotificationStrategy):
    """macOS notification implementation."""

    def play_sound(self, sound_name: str) -> bool:
        # Implementation
        pass

    def is_available(self) -> bool:
        # Implementation
        pass

    def show_message(self, title: str, message: str, icon_type: int = 0) -> bool:
        # Implementation
        pass


class LinuxNotificationStrategy(NotificationStrategy):
    """Linux notification implementation."""

    def play_sound(self, sound_name: str) -> bool:
        # Implementation
        pass

    def is_available(self) -> bool:
        # Implementation
        pass

    def show_message(self, title: str, message: str, icon_type: int = 0) -> bool:
        # Implementation
        pass


class NotificationManager(QObject):
    """Manage application notifications."""

    notification_played = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._strategy = self._create_strategy()
        self._player: Optional[QMediaPlayer] = None
        self._setup_player()

    def _create_strategy(self) -> NotificationStrategy:
        """Create appropriate notification strategy for platform."""
        system = platform.system().lower()
        if system == "windows":
            return WindowsNotificationStrategy()
        # Add other platform strategies here
        return DummyNotificationStrategy()

    def _setup_player(self) -> None:
        """Set up media player for fallback sounds."""
        self._player = QMediaPlayer()
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)

    def _on_media_status_changed(self, status: int) -> None:
        """Handle media status changes."""
        if status == QtMediaConstants.EndOfMedia:
            self._player.stop()

    def play_notification(self, sound_type: str) -> None:
        """Play notification with improved error handling."""
        try:
            if self.settings.get("mute_sound", False):
                return

            sound_name = NotificationConfig.get_sound(sound_type, platform.system().lower())

            if not self._strategy.is_available() or not self._strategy.play_sound(sound_name):
                self._play_fallback(sound_type)

            self.notification_played.emit(sound_type)

        except Exception as e:
            logger.error(f"Notification failed: {e}")
            self.error_signal.emit(str(e))

    def _play_fallback(self, sound_type: str) -> None:
        """Play fallback sound if system sound fails."""
        try:
            if not self._player:
                self._player = QMediaPlayer()

            sound_file = PlatformPaths.get_resource_path() / f"{sound_type}.wav"
            if not sound_file.exists():
                raise FileNotFoundError(f"Fallback sound not found: {sound_file}")

            self._player.setMedia(QMediaContent(QUrl.fromLocalFile(str(sound_file))))
            self._player.play()
        except Exception as e:
            logger.error(f"Fallback sound playback failed: {e}")
            self.error_signal.emit(str(e))


class SystemNotifier:
    """Base class for system-specific notification handling."""

    def play_notification(self, sound_type: str) -> bool:
        """Play system notification sound.

        Args:
            sound_type: Type of notification sound

        Returns:
            bool: True if successful, False otherwise
        """
        raise NotImplementedError


class WindowsNotifier(SystemNotifier):
    """Windows-specific notification handling."""

    def play_notification(self, sound_type: str) -> bool:
        try:
            import winsound

            sound_map = {
                "default": winsound.MB_OK,
                "error": winsound.MB_ICONHAND,
                "complete": winsound.MB_ICONASTERISK,
            }
            winsound.MessageBeep(sound_map.get(sound_type, winsound.MB_OK))
            return True
        except Exception as e:
            logger.error(f"Windows notification failed: {e}")
            return False


class MacOSNotifier(SystemNotifier):
    """macOS-specific notification handling."""

    def play_notification(self, sound_type: str) -> bool:
        try:
            import subprocess

            sound_map = {"default": "Tink", "complete": "Glass", "error": "Basso"}
            sound = sound_map.get(sound_type, "Tink")
            subprocess.run(["afplay", f"/System/Library/Sounds/{sound}.aiff"])
            return True
        except Exception as e:
            logger.error(f"macOS notification failed: {e}")
            return False


class LinuxNotifier(SystemNotifier):
    """Linux-specific notification handling."""

    def play_notification(self, sound_type: str) -> bool:
        try:
            import subprocess

            sound_map = {"default": "bell", "complete": "complete", "error": "dialog-error"}
            sound = sound_map.get(sound_type, "bell")
            subprocess.run(["paplay", f"/usr/share/sounds/freedesktop/stereo/{sound}.oga"])
            return True
        except Exception as e:
            logger.error(f"Linux notification failed: {e}")
            return False

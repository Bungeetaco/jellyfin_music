"""Platform-independent notification handling."""

import platform
import logging
from typing import Optional
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtMultimedia import QSound, QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from .platform_utils import PlatformPaths
from .config import ConfigManager
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class NotificationStrategy(ABC):
    """Abstract base class for platform-specific notification strategies."""
    
    @abstractmethod
    def play_sound(self, sound_name: str) -> bool:
        """Play platform-specific notification sound."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the notification system is available."""
        pass

class WindowsNotificationStrategy(NotificationStrategy):
    def play_sound(self, sound_name: str) -> bool:
        try:
            import winsound
            winsound.PlaySound(sound_name, winsound.SND_ALIAS)
            return True
        except Exception as e:
            logger.debug(f"Windows sound failed: {e}")
            return False

    def is_available(self) -> bool:
        try:
            import winreg
            winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"AppEvents\Schemes")
            return True
        except Exception:
            return False

class NotificationManager(QObject):
    """Enhanced cross-platform notification management."""
    
    error_signal = pyqtSignal(str)
    notification_played = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize notification manager."""
        super().__init__()
        self.config = ConfigManager()
        self.settings = self.config.load()
        self._strategy = self._create_strategy()
        self._fallback_player = None

    def _create_strategy(self) -> NotificationStrategy:
        """Create appropriate notification strategy for platform."""
        system = platform.system().lower()
        if system == "windows":
            return WindowsNotificationStrategy()
        elif system == "darwin":
            return MacNotificationStrategy()
        else:
            return LinuxNotificationStrategy()

    def play_notification(self, sound_type: str) -> None:
        """Play notification with improved error handling."""
        try:
            if self.settings.get("mute_sound", False):
                return

            sound_name = NotificationConfig.get_sound(
                sound_type, 
                platform.system().lower()
            )

            if not self._strategy.is_available() or not self._strategy.play_sound(sound_name):
                self._play_fallback(sound_type)
            
            self.notification_played.emit(sound_type)
            
        except Exception as e:
            logger.error(f"Notification failed: {e}")
            self.error_signal.emit(str(e))

    def _play_fallback(self, sound_type: str) -> None:
        """Play fallback sound if system sound fails."""
        try:
            if not self._fallback_player:
                self._fallback_player = QMediaPlayer()
            
            sound_file = PlatformPaths.get_resource_path() / f"{sound_type}.wav"
            if not sound_file.exists():
                raise FileNotFoundError(f"Fallback sound not found: {sound_file}")
                
            self._fallback_player.setMedia(
                QMediaContent(QUrl.fromLocalFile(str(sound_file)))
            )
            self._fallback_player.play()
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
                "complete": winsound.MB_ICONASTERISK
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
            sound_map = {
                "default": "Tink",
                "complete": "Glass",
                "error": "Basso"
            }
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
            sound_map = {
                "default": "bell",
                "complete": "complete",
                "error": "dialog-error"
            }
            sound = sound_map.get(sound_type, "bell")
            subprocess.run(["paplay", f"/usr/share/sounds/freedesktop/stereo/{sound}.oga"])
            return True
        except Exception as e:
            logger.error(f"Linux notification failed: {e}")
            return False 
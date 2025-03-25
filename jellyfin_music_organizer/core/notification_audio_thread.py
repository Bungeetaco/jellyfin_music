"""
Thread for playing notification sounds.
"""

from typing import Optional
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import sys
import os

class NotificationAudioThread(QThread):
    """
    A QThread subclass that handles playing notification sounds.
    
    This thread:
    1. Loads the specified audio file
    2. Plays the notification sound
    3. Handles cleanup when finished
    
    Signals:
        kill_thread_signal (str): Emitted to signal thread termination
    """
    
    kill_thread_signal: pyqtSignal = pyqtSignal(str)

    def __init__(self, audio_file_name: str) -> None:
        """
        Initialize the NotificationAudioThread.
        
        Args:
            audio_file_name: Name of the audio file to play (without extension)
        """
        super().__init__()
        self.audio_file_name = audio_file_name
        self.media_player: QMediaPlayer = QMediaPlayer()
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

    def run(self) -> None:
        """
        Main thread execution method.
        
        This method:
        1. Constructs the path to the audio file
        2. Sets up the media player
        3. Plays the notification sound
        """
        base_path: str = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        audio_path: str = os.path.join(base_path, f"notification_audio/{self.audio_file_name}.wav")

        # Set media content and play the audio using QMediaPlayer
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(audio_path)))
        self.media_player.play()

    def on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        """
        Handle media status changes.
        
        Args:
            status: Current status of the media player
        """
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.stop()
            self.media_player.deleteLater()
            self.kill_thread_signal.emit('notification')

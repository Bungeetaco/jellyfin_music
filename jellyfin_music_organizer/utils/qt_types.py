"""Type stubs for Qt-related attributes."""

from typing import Union, Optional
from typing_extensions import TypeAlias
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QMouseEvent
from PyQt5.QtWidgets import QWidget
from PyQt5.QtMultimedia import QMediaPlayer
from .typing_compat import WindowFlags, KeyboardModifier, Alignment

# Qt type aliases
WindowFlags = TypeAlias = Union[Qt.WindowFlags, Qt.WindowType]
KeyboardModifier = TypeAlias = Union[Qt.KeyboardModifier, Qt.KeyboardModifiers]
Alignment = TypeAlias = Union[Qt.Alignment, Qt.AlignmentFlag]
MouseButton = TypeAlias = Qt.MouseButton

class QtConstants:
    """Qt constants for type-safe access."""
    
    # Window flags
    Window: WindowFlags = Qt.Window
    Dialog: WindowFlags = Qt.Dialog
    FramelessWindowHint: WindowFlags = Qt.FramelessWindowHint
    WindowStaysOnTopHint: WindowFlags = Qt.WindowStaysOnTopHint

    # Button flags
    LeftButton: MouseButton = Qt.LeftButton

    # Alignment flags
    AlignRight: Alignment = Qt.AlignRight
    AlignBottom: Alignment = Qt.AlignBottom
    AlignCenter: Alignment = Qt.AlignCenter

    # Window attributes
    WA_TranslucentBackground: int = Qt.WA_TranslucentBackground
    WA_MacShowFocusRect: int = Qt.WA_MacShowFocusRect
    WA_MacAlwaysShowToolWindow: int = Qt.WA_MacAlwaysShowToolWindow

    # Application attributes
    AA_EnableHighDpiScaling: int = Qt.AA_EnableHighDpiScaling
    AA_UseHighDpiPixmaps: int = Qt.AA_UseHighDpiPixmaps

    # Modifiers
    MetaModifier: KeyboardModifier = Qt.MetaModifier
    ControlModifier: KeyboardModifier = Qt.ControlModifier

class QtMediaConstants:
    """Qt multimedia constants."""
    PlayingState: int = QMediaPlayer.PlayingState
    EndOfMedia: int = QMediaPlayer.EndOfMedia

# Global instances for easy access
Qt = QtConstants()
QMediaPlayerConst = QtMediaConstants()

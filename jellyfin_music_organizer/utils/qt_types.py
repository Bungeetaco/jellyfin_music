"""Type stubs for Qt-related attributes."""

from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer

# Define each type alias only once and remove duplicates
WindowFlags = Union[Qt.WindowFlags, Qt.WindowType]
KeyboardModifier = Union[Qt.KeyboardModifier, Qt.KeyboardModifiers]
Alignment = Union[Qt.Alignment, Qt.AlignmentFlag]
MouseButton = Qt.MouseButton


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

"""Type stubs for Qt-related attributes."""

from typing import Type, TypeVar, Union

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import QApplication, QWidget
from typing_extensions import TypeAlias

# Type aliases
WindowFlags: TypeAlias = Union[Qt.WindowFlags, Qt.WindowType]
WindowType: TypeAlias = Qt.WindowType
KeyboardModifier: TypeAlias = Union[Qt.KeyboardModifier, Qt.KeyboardModifiers]
ApplicationAttribute: TypeAlias = Qt.ApplicationAttribute
WidgetAttribute: TypeAlias = Qt.WidgetAttribute


# Qt constants wrapper
class QtConstants:
    """Qt constants for type-safe access."""

    # Window flags
    Window = Qt.WindowType.Window
    Dialog = Qt.WindowType.Dialog
    FramelessWindowHint = Qt.WindowType.FramelessWindowHint
    WindowStaysOnTopHint = Qt.WindowType.WindowStaysOnTopHint

    # Button flags
    LeftButton = Qt.MouseButton.LeftButton

    # Alignment flags
    AlignRight = Qt.AlignmentFlag.AlignRight
    AlignBottom = Qt.AlignmentFlag.AlignBottom
    AlignCenter = Qt.AlignmentFlag.AlignCenter

    # Window attributes
    WA_TranslucentBackground = Qt.WidgetAttribute.WA_TranslucentBackground
    WA_MacShowFocusRect = Qt.WidgetAttribute.WA_MacShowFocusRect
    WA_MacAlwaysShowToolWindow = Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow

    # Application attributes
    AA_EnableHighDpiScaling = Qt.ApplicationAttribute.AA_EnableHighDpiScaling
    AA_UseHighDpiPixmaps = Qt.ApplicationAttribute.AA_UseHighDpiPixmaps

    # Modifiers
    MetaModifier = Qt.KeyboardModifier.MetaModifier
    ControlModifier = Qt.KeyboardModifier.ControlModifier

    # Media player states
    PlayingState = QMediaPlayer.State.PlayingState
    EndOfMedia = QMediaPlayer.MediaStatus.EndOfMedia


# Global instances for easy access
Qt = QtConstants()
QMediaPlayerConst = QtConstants()

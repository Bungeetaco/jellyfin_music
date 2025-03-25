"""Type stubs for Qt-related attributes."""

from typing import TypeAlias, Union

from PyQt5.QtCore import Qt

# Qt Enums
WindowType: TypeAlias = Union[Qt.WindowType, Qt.WindowFlags]

# Qt Attributes that mypy can't detect
setattr(Qt, "Window", Qt.WindowType.Window)
setattr(Qt, "Dialog", Qt.WindowType.Dialog)
setattr(Qt, "FramelessWindowHint", Qt.WindowType.FramelessWindowHint)
setattr(Qt, "WindowStaysOnTopHint", Qt.WindowType.WindowStaysOnTopHint)
setattr(Qt, "WA_MacShowFocusRect", "WA_MacShowFocusRect")
setattr(Qt, "WA_MacAlwaysShowToolWindow", "WA_MacAlwaysShowToolWindow")
setattr(Qt, "WA_TranslucentBackground", "WA_TranslucentBackground")
setattr(Qt, "AA_EnableHighDpiScaling", "AA_EnableHighDpiScaling")
setattr(Qt, "AA_UseHighDpiPixmaps", "AA_UseHighDpiPixmaps")
setattr(Qt, "LeftButton", Qt.MouseButton.LeftButton)
setattr(Qt, "AlignRight", Qt.AlignmentFlag.AlignRight)
setattr(Qt, "AlignBottom", Qt.AlignmentFlag.AlignBottom)
setattr(Qt, "AlignCenter", Qt.AlignmentFlag.AlignCenter)

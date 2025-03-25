from typing import Any, List, TypeVar, Union

from typing_extensions import TypeAlias
from PyQt5.QtCore import Qt

try:
    from typing import ParamSpec
except ImportError:
    from typing_extensions import ParamSpec

# Qt-specific type aliases
WindowFlags: TypeAlias = Union[Qt.WindowFlags, Qt.WindowType]
KeyboardModifier: TypeAlias = Union[Qt.KeyboardModifier, Qt.KeyboardModifiers]
Alignment: TypeAlias = Union[Qt.Alignment, Qt.AlignmentFlag]
WindowType: TypeAlias = int
MetadataValue: TypeAlias = Union[str, List[str], Any]

# Common type variables
T = TypeVar("T")
P = ParamSpec("P")

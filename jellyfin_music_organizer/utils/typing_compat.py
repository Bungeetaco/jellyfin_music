from typing import Any, List, TypeVar, Union

from PyQt5.QtCore import Qt
from typing_extensions import ParamSpec, TypeAlias

# Qt-specific type aliases
WindowFlags: TypeAlias = Union[Qt.WindowFlags, Qt.WindowType]
KeyboardModifier: TypeAlias = Union[Qt.KeyboardModifier, Qt.KeyboardModifiers]
Alignment: TypeAlias = Union[Qt.Alignment, Qt.AlignmentFlag]
WindowType: TypeAlias = int
MetadataValue: TypeAlias = Union[str, List[str], Any]

# Common type variables
T = TypeVar("T")
P = ParamSpec("P")

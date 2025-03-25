from typing import Any, List, TypeVar, Union

try:
    from typing import ParamSpec, TypeAlias
except ImportError:
    from typing_extensions import ParamSpec, TypeAlias

# Qt-specific type aliases
WindowFlags = TypeAlias = int
KeyboardModifier = TypeAlias = int
Alignment = TypeAlias = int
WindowType = TypeAlias = int
MetadataValue = TypeAlias = Union[str, List[str], Any]

# Common type variables
T = TypeVar("T")
P = ParamSpec("P")

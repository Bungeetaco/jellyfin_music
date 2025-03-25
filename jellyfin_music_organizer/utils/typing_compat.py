import sys
from typing import Any, Union, List, Dict, Optional, TypeVar, Callable
try:
    from typing import TypeAlias, ParamSpec
except ImportError:
    from typing_extensions import TypeAlias, ParamSpec

# Qt-specific type aliases
WindowFlags = TypeAlias = int
KeyboardModifier = TypeAlias = int
Alignment = TypeAlias = int
WindowType = TypeAlias = int
MetadataValue = TypeAlias = Union[str, List[str], Any]

# Common type variables
T = TypeVar('T')
P = ParamSpec('P') 
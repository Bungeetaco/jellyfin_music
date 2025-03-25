"""Type definitions for metadata handling."""

from typing import Any, Dict, List, Protocol, TypeVar, Union

from typing_extensions import TypeAlias

T = TypeVar("T")


class MetadataProvider(Protocol):
    """Protocol for metadata providers."""

    def __getitem__(self, key: str) -> Any: ...
    def get(self, key: str, default: Any = None) -> Any: ...


class ASFAttribute(Protocol):
    """Protocol for ASF attributes."""

    def __getitem__(self, index: int) -> str: ...
    def __len__(self) -> int: ...


# Type aliases for metadata values
MetadataValue = TypeAlias = Union[str, List[str], ASFAttribute]
MetadataDict = TypeAlias = Dict[str, MetadataValue]

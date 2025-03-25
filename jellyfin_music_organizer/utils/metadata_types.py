"""Type definitions for metadata handling."""

from typing import Any, Dict, Protocol, Union

from mutagen.asf import ASFUnicodeAttribute


class MutagenFile(Protocol):
    """Protocol for mutagen.File interface."""

    def items(self) -> Dict[str, Any]: ...
    def get(self, key: str, default: Any = None) -> Any: ...


MetadataValue = Union[str, list[str], ASFUnicodeAttribute]
MetadataDict = Dict[str, MetadataValue]

"""Resource management utilities."""

import logging
from contextlib import contextmanager
from typing import Any, Callable, Dict, Generator, Optional, TypeVar, Generic
from pathlib import Path

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ResourceManager(Generic[T]):
    """Type-safe resource management."""

    def __init__(self) -> None:
        self._resources: Dict[str, T] = {}
        self._cleanup_handlers: Dict[str, Callable[[T], None]] = {}

    def register(
        self,
        resource_id: str,
        resource: T,
        cleanup_handler: Optional[Callable[[T], None]] = None
    ) -> None:
        """Register a resource with optional cleanup."""
        if resource_id in self._resources:
            self.cleanup(resource_id)
        self._resources[resource_id] = resource
        if cleanup_handler:
            self._cleanup_handlers[resource_id] = cleanup_handler

    def get(self, resource_id: str) -> Optional[T]:
        """Get a registered resource."""
        return self._resources.get(resource_id)

    def cleanup(self, resource_id: str) -> None:
        """Clean up a specific resource."""
        if resource_id in self._resources:
            resource = self._resources[resource_id]
            if resource_id in self._cleanup_handlers:
                try:
                    self._cleanup_handlers[resource_id](resource)
                except Exception as e:
                    logger.error(f"Cleanup error for {resource_id}: {e}")
            del self._resources[resource_id]
            self._cleanup_handlers.pop(resource_id, None)

    @contextmanager
    def managed_resource(
        self,
        resource_id: str,
        resource: T,
        cleanup_handler: Optional[Callable[[T], None]] = None
    ) -> Generator[T, None, None]:
        """Context manager for temporary resources."""
        try:
            self.register(resource_id, resource, cleanup_handler)
            yield resource
        finally:
            self.cleanup(resource_id)

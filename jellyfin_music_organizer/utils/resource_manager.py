"""Resource management utilities."""

import logging
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional, TypeVar, Generator

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ResourceManager:
    """Manage application resources and cleanup."""

    def __init__(self) -> None:
        self._resources: Dict[str, Any] = {}
        self._cleanup_handlers: Dict[str, Callable[[Any], None]] = {}

    def register(
        self, resource_id: str, resource: Any, cleanup_handler: Optional[Callable] = None
    ) -> None:
        """Register a resource with optional cleanup handler."""
        self._resources[resource_id] = resource
        if cleanup_handler:
            self._cleanup_handlers[resource_id] = cleanup_handler

    def cleanup(self) -> None:
        """Clean up all registered resources."""
        for resource_id in list(self._resources.keys()):
            self._cleanup_resource(resource_id)

    def _cleanup_resource(self, resource_id: str) -> None:
        """Clean up a specific resource."""
        try:
            resource = self._resources.pop(resource_id, None)
            if resource:
                handler = self._cleanup_handlers.pop(resource_id, None)
                if handler:
                    handler(resource)
                elif hasattr(resource, "close"):
                    resource.close()
                elif hasattr(resource, "cleanup"):
                    resource.cleanup()
                elif hasattr(resource, "deleteLater"):
                    resource.deleteLater()
        except Exception as e:
            logger.error(f"Failed to clean up resource {resource_id}: {e}")

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

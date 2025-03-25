"""Resource management utilities."""

from typing import Any, Callable, Optional
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class ResourceManager:
    """Manage application resources and cleanup."""
    
    def __init__(self) -> None:
        self._resources: Dict[str, Any] = {}
        self._cleanup_handlers: Dict[str, Callable] = {}

    def register(
        self, 
        resource_id: str, 
        resource: Any, 
        cleanup_handler: Optional[Callable] = None
    ) -> None:
        """Register a resource with optional cleanup handler."""
        self._resources[resource_id] = resource
        if cleanup_handler:
            self._cleanup_handlers[resource_id] = cleanup_handler

    def cleanup(self, resource_id: Optional[str] = None) -> None:
        """Clean up specific or all resources."""
        if resource_id:
            self._cleanup_resource(resource_id)
        else:
            for rid in list(self._resources.keys()):
                self._cleanup_resource(rid)

    def _cleanup_resource(self, resource_id: str) -> None:
        """Clean up a specific resource."""
        try:
            resource = self._resources.pop(resource_id, None)
            if resource:
                handler = self._cleanup_handlers.pop(resource_id, None)
                if handler:
                    handler(resource)
                elif hasattr(resource, 'close'):
                    resource.close()
                elif hasattr(resource, 'cleanup'):
                    resource.cleanup()
                elif hasattr(resource, 'deleteLater'):
                    resource.deleteLater()
        except Exception as e:
            logger.error(f"Failed to clean up resource {resource_id}: {e}")

    @contextmanager
    def managed_resource(self, resource_id: str, resource: Any, cleanup_handler: Optional[Callable] = None):
        """Context manager for temporary resources."""
        try:
            self.register(resource_id, resource, cleanup_handler)
            yield resource
        finally:
            self.cleanup(resource_id) 
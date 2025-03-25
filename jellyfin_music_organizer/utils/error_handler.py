"""Centralized error handling."""

import logging
import traceback
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


def handle_errors(error_message: str, callback: Optional[Callable[[Exception], Any]] = None):
    """Decorator for consistent error handling."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{error_message}: {str(e)}\n" f"Traceback:\n{traceback.format_exc()}")
                if callback:
                    return callback(e)
                raise

        return wrapper

    return decorator


class ResourceManager:
    """Manage application resources and cleanup."""

    def __init__(self) -> None:
        self._resources: List[Any] = []

    def register(self, resource: Any) -> None:
        """Register a resource for cleanup."""
        self._resources.append(resource)

    def cleanup(self) -> None:
        """Clean up all registered resources."""
        for resource in reversed(self._resources):
            try:
                if hasattr(resource, "close"):
                    resource.close()
                elif hasattr(resource, "cleanup"):
                    resource.cleanup()
                elif hasattr(resource, "deleteLater"):
                    resource.deleteLater()
            except Exception as e:
                logger.error(f"Failed to clean up resource: {e}")

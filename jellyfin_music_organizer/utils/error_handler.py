"""Centralized error handling."""

import logging
from functools import wraps
from logging import Logger
from typing import Any, Callable, Dict, List, Optional, ParamSpec, TypeVar, Union

from .typing_compat import P

logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")


def handle_errors(
    logger: Optional[Logger] = None, default_return: Optional[T] = None, reraise: bool = False
) -> Callable[[Callable[P, T]], Callable[P, Union[T, None]]]:
    """Decorator for consistent error handling with proper type hints."""

    def decorator(func: Callable[P, T]) -> Callable[P, Union[T, None]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Union[T, None]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if logger:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                if reraise:
                    raise
                return default_return

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


class ErrorCollector:
    """Collect and manage errors during processing."""

    def __init__(self) -> None:
        self.errors: Dict[str, str] = {}
        self.warnings: Dict[str, str] = {}

    def add_error(self, key: str, message: str) -> None:
        """Add an error message."""
        self.errors[key] = message

    def add_warning(self, key: str, message: str) -> None:
        """Add a warning message."""
        self.warnings[key] = message

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return bool(self.errors)

    def get_error_summary(self) -> str:
        """Get a formatted summary of all errors."""
        return "\n".join(f"{k}: {v}" for k, v in self.errors.items())

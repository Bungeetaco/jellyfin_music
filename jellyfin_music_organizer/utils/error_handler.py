"""Centralized error handling."""

import logging
from functools import wraps
from typing import Any, Callable, Dict, List, TypeVar
from typing_extensions import ParamSpec  # Single import

from typing_extensions import ParamSpec

from .typing_compat import P  # Use shared ParamSpec

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Local TypeVar is fine
P = ParamSpec("P")


def handle_errors(func: Callable[P, T], logger: Optional[logging.Logger] = None) -> Callable[P, T]:
    """Decorator to handle errors in functions."""

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log = logger or logging.getLogger(__name__)
            log.error(f"Error in {func.__name__}: {e}")
            raise

    return wrapper


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
